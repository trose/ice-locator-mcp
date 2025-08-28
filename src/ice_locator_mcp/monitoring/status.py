"""
Status monitoring and health check utilities for ICE Locator MCP Server.
"""

import asyncio
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import structlog
import psutil
import httpx

from ..core.config import Config


class ServiceStatus(Enum):
    """Service status enumeration."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthMetrics:
    """Health metrics for monitoring."""
    status: ServiceStatus = ServiceStatus.UNKNOWN
    uptime_seconds: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    cache_hit_rate: float = 0.0
    request_count: int = 0
    success_rate: float = 0.0
    average_response_time: float = 0.0
    active_connections: int = 0
    proxy_health: Dict[str, Any] = field(default_factory=dict)
    last_check: float = field(default_factory=time.time)


@dataclass
class ServiceAlert:
    """Service alert information."""
    level: str  # info, warning, error, critical
    message: str
    timestamp: float
    component: str
    resolved: bool = False


class StatusMonitor:
    """Monitors system status and health metrics."""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = structlog.get_logger(__name__)
        self.start_time = time.time()
        
        # Metrics tracking
        self.metrics = HealthMetrics()
        self.alerts: List[ServiceAlert] = []
        self.performance_history: List[Dict[str, float]] = []
        
        # Monitoring state
        self.monitoring_active = False
        self.monitor_task: Optional[asyncio.Task] = None
        
        # Thresholds
        self.thresholds = {
            "memory_mb": 500,
            "cpu_percent": 80,
            "response_time_ms": 5000,
            "success_rate": 0.8,
            "cache_hit_rate": 0.6
        }
    
    async def start_monitoring(self) -> None:
        """Start continuous monitoring."""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitor_task = asyncio.create_task(self._monitoring_loop())
        self.logger.info("Status monitoring started")
    
    async def stop_monitoring(self) -> None:
        """Stop continuous monitoring."""
        self.monitoring_active = False
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Status monitoring stopped")
    
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                await self._collect_metrics()
                await self._check_health()
                await self._update_performance_history()
                
                # Sleep for monitoring interval
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("Monitoring error", error=str(e))
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _collect_metrics(self) -> None:
        """Collect current system metrics."""
        try:
            # Update uptime
            self.metrics.uptime_seconds = time.time() - self.start_time
            
            # System metrics
            self.metrics.memory_usage_mb = psutil.Process().memory_info().rss / 1024 / 1024
            self.metrics.cpu_usage_percent = psutil.Process().cpu_percent()
            
            # Update timestamp
            self.metrics.last_check = time.time()
            
        except Exception as e:
            self.logger.warning("Failed to collect metrics", error=str(e))
    
    async def _check_health(self) -> None:
        """Check system health and generate alerts."""
        alerts = []
        
        # Memory check
        if self.metrics.memory_usage_mb > self.thresholds["memory_mb"]:
            alerts.append(ServiceAlert(
                level="warning",
                message=f"High memory usage: {self.metrics.memory_usage_mb:.1f}MB",
                timestamp=time.time(),
                component="system"
            ))
        
        # CPU check
        if self.metrics.cpu_usage_percent > self.thresholds["cpu_percent"]:
            alerts.append(ServiceAlert(
                level="warning",
                message=f"High CPU usage: {self.metrics.cpu_usage_percent:.1f}%",
                timestamp=time.time(),
                component="system"
            ))
        
        # Response time check
        if self.metrics.average_response_time > self.thresholds["response_time_ms"]:
            alerts.append(ServiceAlert(
                level="warning",
                message=f"Slow response time: {self.metrics.average_response_time:.0f}ms",
                timestamp=time.time(),
                component="performance"
            ))
        
        # Success rate check
        if self.metrics.success_rate < self.thresholds["success_rate"]:
            alerts.append(ServiceAlert(
                level="error",
                message=f"Low success rate: {self.metrics.success_rate:.1%}",
                timestamp=time.time(),
                component="reliability"
            ))
        
        # Add new alerts
        for alert in alerts:
            self.alerts.append(alert)
            self.logger.warning(
                "Health check alert",
                level=alert.level,
                component=alert.component,
                message=alert.message
            )
        
        # Determine overall status
        if any(a.level == "critical" for a in alerts):
            self.metrics.status = ServiceStatus.UNHEALTHY
        elif any(a.level == "error" for a in alerts):
            self.metrics.status = ServiceStatus.DEGRADED
        elif any(a.level == "warning" for a in alerts):
            self.metrics.status = ServiceStatus.DEGRADED
        else:
            self.metrics.status = ServiceStatus.HEALTHY
    
    async def _update_performance_history(self) -> None:
        """Update performance metrics history."""
        entry = {
            "timestamp": time.time(),
            "memory_mb": self.metrics.memory_usage_mb,
            "cpu_percent": self.metrics.cpu_usage_percent,
            "response_time": self.metrics.average_response_time,
            "success_rate": self.metrics.success_rate,
            "request_count": self.metrics.request_count
        }
        
        self.performance_history.append(entry)
        
        # Keep only last 24 hours (assuming 30s intervals = 2880 entries)
        if len(self.performance_history) > 2880:
            self.performance_history = self.performance_history[-2880:]
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get current health status."""
        return {
            "status": self.metrics.status.value,
            "uptime_seconds": self.metrics.uptime_seconds,
            "uptime_human": self._format_uptime(self.metrics.uptime_seconds),
            "memory_usage_mb": round(self.metrics.memory_usage_mb, 1),
            "cpu_usage_percent": round(self.metrics.cpu_usage_percent, 1),
            "request_count": self.metrics.request_count,
            "success_rate": round(self.metrics.success_rate, 3),
            "average_response_time": round(self.metrics.average_response_time, 0),
            "cache_hit_rate": round(self.metrics.cache_hit_rate, 3),
            "active_connections": self.metrics.active_connections,
            "last_check": self.metrics.last_check,
            "alerts_count": len([a for a in self.alerts if not a.resolved])
        }
    
    async def get_detailed_status(self) -> Dict[str, Any]:
        """Get detailed status including alerts and history."""
        status = await self.get_health_status()
        
        # Add alerts
        active_alerts = [
            {
                "level": alert.level,
                "message": alert.message,
                "timestamp": alert.timestamp,
                "component": alert.component,
                "age_seconds": time.time() - alert.timestamp
            }
            for alert in self.alerts 
            if not alert.resolved
        ]
        
        # Add performance trends
        trends = self._calculate_trends()
        
        return {
            **status,
            "alerts": active_alerts,
            "trends": trends,
            "proxy_health": self.metrics.proxy_health,
            "performance_history": self.performance_history[-100:]  # Last 100 entries
        }
    
    def _calculate_trends(self) -> Dict[str, str]:
        """Calculate performance trends."""
        if len(self.performance_history) < 10:
            return {}
        
        recent = self.performance_history[-10:]
        older = self.performance_history[-20:-10] if len(self.performance_history) >= 20 else []
        
        if not older:
            return {}
        
        trends = {}
        
        # Calculate trend for each metric
        for metric in ["memory_mb", "cpu_percent", "response_time", "success_rate"]:
            recent_avg = sum(entry[metric] for entry in recent) / len(recent)
            older_avg = sum(entry[metric] for entry in older) / len(older)
            
            if recent_avg > older_avg * 1.1:
                trends[metric] = "increasing"
            elif recent_avg < older_avg * 0.9:
                trends[metric] = "decreasing"
            else:
                trends[metric] = "stable"
        
        return trends
    
    def _format_uptime(self, seconds: float) -> str:
        """Format uptime in human readable format."""
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            return f"{seconds/60:.0f}m"
        elif seconds < 86400:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
        else:
            days = int(seconds // 86400)
            hours = int((seconds % 86400) // 3600)
            return f"{days}d {hours}h"
    
    async def update_request_metrics(self, success: bool, response_time: float) -> None:
        """Update request-related metrics."""
        self.metrics.request_count += 1
        
        # Update success rate (exponential moving average)
        if self.metrics.request_count == 1:
            self.metrics.success_rate = 1.0 if success else 0.0
        else:
            alpha = 0.1  # Smoothing factor
            new_value = 1.0 if success else 0.0
            self.metrics.success_rate = (
                alpha * new_value + (1 - alpha) * self.metrics.success_rate
            )
        
        # Update average response time
        if self.metrics.average_response_time == 0:
            self.metrics.average_response_time = response_time
        else:
            alpha = 0.1
            self.metrics.average_response_time = (
                alpha * response_time + (1 - alpha) * self.metrics.average_response_time
            )
    
    async def update_cache_metrics(self, hit: bool) -> None:
        """Update cache-related metrics."""
        # Update cache hit rate
        if not hasattr(self, '_cache_requests'):
            self._cache_requests = 0
            self._cache_hits = 0
        
        self._cache_requests += 1
        if hit:
            self._cache_hits += 1
        
        self.metrics.cache_hit_rate = self._cache_hits / self._cache_requests
    
    async def update_proxy_health(self, proxy_health: Dict[str, Any]) -> None:
        """Update proxy health information."""
        self.metrics.proxy_health = proxy_health
    
    async def resolve_alert(self, alert_index: int) -> bool:
        """Mark an alert as resolved."""
        if 0 <= alert_index < len(self.alerts):
            self.alerts[alert_index].resolved = True
            return True
        return False
    
    async def clear_resolved_alerts(self) -> int:
        """Clear all resolved alerts and return count."""
        before_count = len(self.alerts)
        self.alerts = [a for a in self.alerts if not a.resolved]
        return before_count - len(self.alerts)


class HealthEndpoint:
    """HTTP endpoint for health checks."""
    
    def __init__(self, monitor: StatusMonitor):
        self.monitor = monitor
    
    async def health_check(self) -> Dict[str, Any]:
        """Basic health check endpoint."""
        status = await self.monitor.get_health_status()
        
        # Simple health check format
        return {
            "status": status["status"],
            "timestamp": time.time(),
            "uptime": status["uptime_human"],
            "version": "0.1.0"  # Should come from config
        }
    
    async def detailed_health(self) -> Dict[str, Any]:
        """Detailed health information."""
        return await self.monitor.get_detailed_status()
    
    async def metrics(self) -> Dict[str, Any]:
        """Prometheus-style metrics."""
        status = await self.monitor.get_health_status()
        
        return {
            "ice_locator_uptime_seconds": status["uptime_seconds"],
            "ice_locator_memory_usage_bytes": status["memory_usage_mb"] * 1024 * 1024,
            "ice_locator_cpu_usage_ratio": status["cpu_usage_percent"] / 100,
            "ice_locator_requests_total": status["request_count"],
            "ice_locator_success_rate": status["success_rate"],
            "ice_locator_response_time_seconds": status["average_response_time"] / 1000,
            "ice_locator_cache_hit_rate": status["cache_hit_rate"],
            "ice_locator_active_connections": status["active_connections"]
        }