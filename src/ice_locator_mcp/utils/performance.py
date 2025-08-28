"""
Performance Monitoring and Metrics Collection for ICE Locator MCP Server.

This module provides comprehensive performance tracking, metrics collection,
and system monitoring capabilities.
"""

import asyncio
import json
import time
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Tuple
import psutil
import structlog


@dataclass
class PerformanceMetric:
    """Single performance metric data point."""
    timestamp: float
    metric_name: str
    value: float
    unit: str
    tags: Dict[str, str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)


@dataclass
class RequestMetrics:
    """Metrics for a single request."""
    request_id: str
    start_time: float
    end_time: Optional[float] = None
    status: str = "in_progress"
    error: Optional[str] = None
    
    # Performance metrics
    total_duration: Optional[float] = None
    network_time: Optional[float] = None
    processing_time: Optional[float] = None
    cache_hit: bool = False
    
    # Resource usage
    memory_usage: Optional[float] = None
    cpu_usage: Optional[float] = None
    
    # Request details
    search_type: Optional[str] = None
    result_count: Optional[int] = None
    proxy_used: Optional[str] = None
    
    def complete(self, status: str = "completed", error: Optional[str] = None) -> None:
        """Mark request as completed."""
        self.end_time = time.time()
        self.total_duration = self.end_time - self.start_time
        self.status = status
        self.error = error


@dataclass
class SystemMetrics:
    """System-level performance metrics."""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    disk_usage_percent: float
    network_bytes_sent: int
    network_bytes_recv: int
    active_connections: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class MetricsCollector:
    """Collects and aggregates performance metrics."""
    
    def __init__(self, max_history: int = 1000):
        self.logger = structlog.get_logger(__name__)
        self.max_history = max_history
        
        # Metrics storage
        self.request_metrics: deque = deque(maxlen=max_history)
        self.system_metrics: deque = deque(maxlen=max_history)
        self.custom_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history))
        
        # Current request tracking
        self.active_requests: Dict[str, RequestMetrics] = {}
        
        # Aggregated statistics
        self.stats_cache: Dict[str, Any] = {}
        self.stats_cache_time: float = 0.0
        self.stats_cache_ttl: float = 30.0  # 30 seconds
        
        # System monitoring
        self.system_monitor_task: Optional[asyncio.Task] = None
        self.monitoring_active = False
        
    async def start_monitoring(self) -> None:
        """Start system monitoring."""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.system_monitor_task = asyncio.create_task(self._system_monitor_loop())
            self.logger.info("Performance monitoring started")
    
    async def stop_monitoring(self) -> None:
        """Stop system monitoring."""
        self.monitoring_active = False
        if self.system_monitor_task:
            self.system_monitor_task.cancel()
            try:
                await self.system_monitor_task
            except asyncio.CancelledError:
                pass
        self.logger.info("Performance monitoring stopped")
    
    def start_request(self, request_id: str, search_type: str = None) -> RequestMetrics:
        """Start tracking a new request."""
        metrics = RequestMetrics(
            request_id=request_id,
            start_time=time.time(),
            search_type=search_type
        )
        self.active_requests[request_id] = metrics
        return metrics
    
    def complete_request(self, request_id: str, status: str = "completed", 
                        error: Optional[str] = None, **kwargs) -> None:
        """Complete request tracking."""
        if request_id in self.active_requests:
            metrics = self.active_requests[request_id]
            metrics.complete(status, error)
            
            # Update with additional metrics
            for key, value in kwargs.items():
                if hasattr(metrics, key):
                    setattr(metrics, key, value)
            
            # Move to history
            self.request_metrics.append(metrics)
            del self.active_requests[request_id]
            
            self.logger.debug(
                "Request completed",
                request_id=request_id,
                duration=metrics.total_duration,
                status=status
            )
    
    def record_metric(self, name: str, value: float, unit: str = "", 
                     tags: Optional[Dict[str, str]] = None) -> None:
        """Record a custom metric."""
        metric = PerformanceMetric(
            timestamp=time.time(),
            metric_name=name,
            value=value,
            unit=unit,
            tags=tags or {}
        )
        self.custom_metrics[name].append(metric)
    
    def get_request_stats(self, last_n_minutes: int = 60) -> Dict[str, Any]:
        """Get request statistics for the last N minutes."""
        cutoff_time = time.time() - (last_n_minutes * 60)
        
        # Filter recent requests
        recent_requests = [
            req for req in self.request_metrics 
            if req.start_time >= cutoff_time
        ]
        
        if not recent_requests:
            return {
                'total_requests': 0,
                'time_period_minutes': last_n_minutes
            }
        
        # Calculate statistics
        completed_requests = [req for req in recent_requests if req.status == "completed"]
        failed_requests = [req for req in recent_requests if req.status == "failed"]
        
        durations = [req.total_duration for req in completed_requests if req.total_duration]
        
        stats = {
            'time_period_minutes': last_n_minutes,
            'total_requests': len(recent_requests),
            'completed_requests': len(completed_requests),
            'failed_requests': len(failed_requests),
            'success_rate': len(completed_requests) / len(recent_requests) if recent_requests else 0,
            'requests_per_minute': len(recent_requests) / last_n_minutes,
        }
        
        if durations:
            stats.update({
                'avg_response_time': sum(durations) / len(durations),
                'min_response_time': min(durations),
                'max_response_time': max(durations),
                'p95_response_time': self._calculate_percentile(durations, 0.95),
                'p99_response_time': self._calculate_percentile(durations, 0.99)
            })
        
        # Group by search type
        by_search_type = defaultdict(int)
        for req in recent_requests:
            if req.search_type:
                by_search_type[req.search_type] += 1
        stats['by_search_type'] = dict(by_search_type)
        
        # Cache hit rate
        cache_hits = sum(1 for req in completed_requests if req.cache_hit)
        stats['cache_hit_rate'] = cache_hits / len(completed_requests) if completed_requests else 0
        
        return stats
    
    def get_system_stats(self, last_n_minutes: int = 10) -> Dict[str, Any]:
        """Get system statistics for the last N minutes."""
        cutoff_time = time.time() - (last_n_minutes * 60)
        
        # Filter recent metrics
        recent_metrics = [
            metric for metric in self.system_metrics 
            if metric.timestamp >= cutoff_time
        ]
        
        if not recent_metrics:
            return {
                'time_period_minutes': last_n_minutes,
                'samples': 0
            }
        
        # Calculate averages
        cpu_values = [m.cpu_percent for m in recent_metrics]
        memory_values = [m.memory_percent for m in recent_metrics]
        disk_values = [m.disk_usage_percent for m in recent_metrics]
        
        return {
            'time_period_minutes': last_n_minutes,
            'samples': len(recent_metrics),
            'avg_cpu_percent': sum(cpu_values) / len(cpu_values),
            'max_cpu_percent': max(cpu_values),
            'avg_memory_percent': sum(memory_values) / len(memory_values),
            'max_memory_percent': max(memory_values),
            'avg_disk_usage_percent': sum(disk_values) / len(disk_values),
            'latest_memory_mb': recent_metrics[-1].memory_used_mb,
            'active_connections': recent_metrics[-1].active_connections
        }
    
    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics."""
        # Use cache if recent
        current_time = time.time()
        if (current_time - self.stats_cache_time) < self.stats_cache_ttl and self.stats_cache:
            return self.stats_cache
        
        stats = {
            'timestamp': current_time,
            'request_stats': self.get_request_stats(60),  # Last hour
            'system_stats': self.get_system_stats(10),    # Last 10 minutes
            'active_requests': len(self.active_requests),
            'total_requests_tracked': len(self.request_metrics),
            'monitoring_active': self.monitoring_active
        }
        
        # Custom metrics summary
        custom_stats = {}
        for metric_name, metric_history in self.custom_metrics.items():
            if metric_history:
                values = [m.value for m in metric_history]
                custom_stats[metric_name] = {
                    'current': values[-1],
                    'average': sum(values) / len(values),
                    'min': min(values),
                    'max': max(values),
                    'samples': len(values)
                }
        stats['custom_metrics'] = custom_stats
        
        # Update cache
        self.stats_cache = stats
        self.stats_cache_time = current_time
        
        return stats
    
    async def _system_monitor_loop(self) -> None:
        """Background loop for system monitoring."""
        while self.monitoring_active:
            try:
                metrics = await self._collect_system_metrics()
                self.system_metrics.append(metrics)
                
                # Sleep for monitoring interval
                await asyncio.sleep(30)  # Collect every 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("System monitoring error", error=str(e))
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics."""
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        
        # CPU and memory
        cpu_percent = await loop.run_in_executor(None, psutil.cpu_percent, 1.0)
        memory = await loop.run_in_executor(None, psutil.virtual_memory)
        disk = await loop.run_in_executor(None, psutil.disk_usage, '/')
        
        # Network
        network = await loop.run_in_executor(None, psutil.net_io_counters)
        
        # Connections (approximate)
        try:
            connections = await loop.run_in_executor(None, len, psutil.net_connections())
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            connections = 0
        
        return SystemMetrics(
            timestamp=time.time(),
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_used_mb=memory.used / (1024 * 1024),
            disk_usage_percent=disk.percent,
            network_bytes_sent=network.bytes_sent if network else 0,
            network_bytes_recv=network.bytes_recv if network else 0,
            active_connections=connections
        )
    
    def _calculate_percentile(self, values: List[float], percentile: float) -> float:
        """Calculate percentile of values."""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = int(percentile * len(sorted_values))
        index = min(index, len(sorted_values) - 1)
        return sorted_values[index]
    
    def export_metrics(self, format: str = "json") -> str:
        """Export metrics in specified format."""
        data = {
            'export_timestamp': time.time(),
            'request_metrics': [req.to_dict() if hasattr(req, 'to_dict') else asdict(req) 
                              for req in list(self.request_metrics)],
            'system_metrics': [metric.to_dict() for metric in list(self.system_metrics)],
            'custom_metrics': {
                name: [metric.to_dict() for metric in list(metrics)]
                for name, metrics in self.custom_metrics.items()
            },
            'stats': self.get_comprehensive_stats()
        }
        
        if format.lower() == "json":
            return json.dumps(data, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported export format: {format}")


class PerformanceProfiler:
    """Detailed performance profiling for specific operations."""
    
    def __init__(self):
        self.logger = structlog.get_logger(__name__)
        self.profiles: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    
    async def profile_operation(self, operation_name: str, operation_func, *args, **kwargs):
        """Profile a specific operation."""
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / (1024 * 1024)  # MB
        
        try:
            result = await operation_func(*args, **kwargs)
            success = True
            error = None
        except Exception as e:
            result = None
            success = False
            error = str(e)
            raise
        finally:
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss / (1024 * 1024)  # MB
            
            profile_data = {
                'timestamp': start_time,
                'operation': operation_name,
                'duration': end_time - start_time,
                'memory_start_mb': start_memory,
                'memory_end_mb': end_memory,
                'memory_delta_mb': end_memory - start_memory,
                'success': success,
                'error': error,
                'args_count': len(args),
                'kwargs_count': len(kwargs)
            }
            
            self.profiles[operation_name].append(profile_data)
            
            self.logger.debug(
                "Operation profiled",
                operation=operation_name,
                duration=profile_data['duration'],
                memory_delta=profile_data['memory_delta_mb'],
                success=success
            )
        
        return result
    
    def get_profile_stats(self, operation_name: str) -> Dict[str, Any]:
        """Get statistics for a specific operation."""
        profiles = self.profiles.get(operation_name, [])
        
        if not profiles:
            return {'operation': operation_name, 'samples': 0}
        
        durations = [p['duration'] for p in profiles]
        memory_deltas = [p['memory_delta_mb'] for p in profiles]
        successes = sum(1 for p in profiles if p['success'])
        
        return {
            'operation': operation_name,
            'samples': len(profiles),
            'success_rate': successes / len(profiles),
            'avg_duration': sum(durations) / len(durations),
            'min_duration': min(durations),
            'max_duration': max(durations),
            'avg_memory_delta_mb': sum(memory_deltas) / len(memory_deltas),
            'total_memory_delta_mb': sum(memory_deltas),
            'recent_profiles': profiles[-10:]  # Last 10 profiles
        }


class PerformanceOptimizer:
    """Analyzes performance data and suggests optimizations."""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.logger = structlog.get_logger(__name__)
    
    def analyze_performance(self) -> Dict[str, Any]:
        """Analyze current performance and suggest optimizations."""
        stats = self.metrics_collector.get_comprehensive_stats()
        
        suggestions = []
        warnings = []
        critical_issues = []
        
        # Analyze request performance
        request_stats = stats.get('request_stats', {})
        if request_stats.get('avg_response_time', 0) > 10.0:  # 10 seconds
            warnings.append("Average response time is high (>10s). Consider optimizing search algorithms.")
        
        if request_stats.get('success_rate', 1.0) < 0.95:  # Less than 95%
            critical_issues.append("Success rate is below 95%. Check error logs and retry mechanisms.")
        
        cache_hit_rate = request_stats.get('cache_hit_rate', 0)
        if cache_hit_rate < 0.3:  # Less than 30%
            suggestions.append("Cache hit rate is low. Consider increasing cache TTL or size.")
        elif cache_hit_rate > 0.8:  # Greater than 80%
            suggestions.append("Excellent cache hit rate! Cache is working effectively.")
        
        # Analyze system performance
        system_stats = stats.get('system_stats', {})
        if system_stats.get('avg_cpu_percent', 0) > 80:
            warnings.append("High CPU usage detected. Consider scaling or optimizing CPU-intensive operations.")
        
        if system_stats.get('avg_memory_percent', 0) > 85:
            critical_issues.append("High memory usage. Risk of out-of-memory errors.")
        
        # Rate limiting analysis
        rpm = request_stats.get('requests_per_minute', 0)
        if rpm > 8:  # Close to typical rate limit
            warnings.append("Request rate is approaching limits. Monitor for rate limiting errors.")
        
        return {
            'analysis_timestamp': time.time(),
            'performance_score': self._calculate_performance_score(stats),
            'suggestions': suggestions,
            'warnings': warnings,
            'critical_issues': critical_issues,
            'optimization_opportunities': self._find_optimization_opportunities(stats)
        }
    
    def _calculate_performance_score(self, stats: Dict[str, Any]) -> int:
        """Calculate overall performance score (0-100)."""
        score = 100
        
        # Request performance factors
        request_stats = stats.get('request_stats', {})
        success_rate = request_stats.get('success_rate', 1.0)
        score *= success_rate  # Reduce score by failure rate
        
        avg_response_time = request_stats.get('avg_response_time', 0)
        if avg_response_time > 5:
            score *= 0.8  # Penalty for slow responses
        elif avg_response_time > 10:
            score *= 0.6  # Higher penalty for very slow responses
        
        # System performance factors
        system_stats = stats.get('system_stats', {})
        cpu_usage = system_stats.get('avg_cpu_percent', 0)
        memory_usage = system_stats.get('avg_memory_percent', 0)
        
        if cpu_usage > 80:
            score *= 0.7
        if memory_usage > 85:
            score *= 0.6
        
        # Cache performance bonus
        cache_hit_rate = request_stats.get('cache_hit_rate', 0)
        if cache_hit_rate > 0.5:
            score *= 1.1  # Bonus for good caching
        
        return max(0, min(100, int(score)))
    
    def _find_optimization_opportunities(self, stats: Dict[str, Any]) -> List[str]:
        """Find specific optimization opportunities."""
        opportunities = []
        
        request_stats = stats.get('request_stats', {})
        
        # Check for optimization patterns
        by_search_type = request_stats.get('by_search_type', {})
        if 'name_based' in by_search_type and by_search_type['name_based'] > by_search_type.get('alien_number', 0) * 2:
            opportunities.append("Consider optimizing name-based searches - they're much more frequent than A-number searches")
        
        # P95 vs average response time
        p95_time = request_stats.get('p95_response_time', 0)
        avg_time = request_stats.get('avg_response_time', 0)
        if p95_time > avg_time * 3:
            opportunities.append("High variance in response times - investigate slow outliers")
        
        # Active connections
        system_stats = stats.get('system_stats', {})
        active_connections = system_stats.get('active_connections', 0)
        if active_connections > 100:
            opportunities.append("Many active connections - consider connection pooling optimization")
        
        return opportunities