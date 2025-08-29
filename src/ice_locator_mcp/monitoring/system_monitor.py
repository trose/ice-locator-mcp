"""
OS-Level Monitoring Integration Module.

Combines MCPcat analytics with system monitoring tools (htop, iostat, netstat, ps)
for comprehensive performance visibility and resource usage tracking.
"""

import asyncio
import json
import subprocess
import time
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field, asdict
from pathlib import Path
import logging
import shutil

import structlog
try:
    import mcpcat
    MCPCAT_AVAILABLE = True
except ImportError:
    mcpcat = None
    MCPCAT_AVAILABLE = False


@dataclass
class SystemMetrics:
    """System performance metrics snapshot."""
    
    timestamp: datetime = field(default_factory=datetime.now)
    
    # CPU metrics
    cpu_percent: float = 0.0
    cpu_count: int = 0
    cpu_freq: Optional[float] = None
    load_average: List[float] = field(default_factory=list)
    
    # Memory metrics
    memory_total: int = 0
    memory_available: int = 0
    memory_percent: float = 0.0
    memory_used: int = 0
    swap_total: int = 0
    swap_used: int = 0
    swap_percent: float = 0.0
    
    # Disk metrics
    disk_total: int = 0
    disk_used: int = 0
    disk_free: int = 0
    disk_percent: float = 0.0
    disk_io_read_bytes: int = 0
    disk_io_write_bytes: int = 0
    disk_io_read_time: int = 0
    disk_io_write_time: int = 0
    
    # Network metrics
    network_bytes_sent: int = 0
    network_bytes_recv: int = 0
    network_packets_sent: int = 0
    network_packets_recv: int = 0
    network_connections: int = 0
    
    # Process metrics (for this specific process)
    process_cpu_percent: float = 0.0
    process_memory_rss: int = 0
    process_memory_vms: int = 0
    process_memory_percent: float = 0.0
    process_num_threads: int = 0
    process_num_fds: int = 0
    process_connections: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data
    
    @property
    def memory_available_gb(self) -> float:
        """Memory available in GB."""
        return self.memory_available / (1024**3)
    
    @property
    def disk_free_gb(self) -> float:
        """Disk free space in GB."""
        return self.disk_free / (1024**3)


@dataclass
class ProcessInfo:
    """Information about a running process."""
    
    pid: int
    name: str
    cpu_percent: float
    memory_rss: int
    memory_vms: int
    memory_percent: float
    num_threads: int
    status: str
    create_time: float
    cmdline: List[str] = field(default_factory=list)
    
    @property
    def memory_rss_mb(self) -> float:
        """Memory RSS in MB."""
        return self.memory_rss / (1024**2)
    
    @property
    def uptime_seconds(self) -> float:
        """Process uptime in seconds."""
        return time.time() - self.create_time


class SystemMonitor:
    """System monitoring integration with MCPcat analytics."""
    
    def __init__(self, mcpcat_options: Optional[Dict[str, Any]] = None,
                 collection_interval: int = 30,
                 storage_path: Optional[Path] = None):
        """Initialize system monitor."""
        self.logger = structlog.get_logger(__name__)
        self.mcpcat_options = mcpcat_options if MCPCAT_AVAILABLE else None
        self.collection_interval = collection_interval
        
        # Storage for metrics
        self.storage_path = storage_path or Path.home() / ".cache" / "ice-locator-mcp" / "system-metrics"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Monitoring state
        self.is_monitoring = False
        self.monitoring_task: Optional[asyncio.Task] = None
        self.current_process = psutil.Process()
        
        # Metrics history
        self.metrics_history: List[SystemMetrics] = []
        self.max_history_size = 1000  # Keep last 1000 metric snapshots
        
        # Tool availability
        self.available_tools = self._check_available_tools()
        
        # Baseline metrics for comparison
        self.baseline_metrics: Optional[SystemMetrics] = None
        
        self.logger.info("System monitor initialized",
                        collection_interval=collection_interval,
                        available_tools=list(self.available_tools.keys()),
                        storage_path=str(self.storage_path))
    
    def _check_available_tools(self) -> Dict[str, bool]:
        """Check which system monitoring tools are available."""
        tools = {
            "htop": shutil.which("htop") is not None,
            "top": shutil.which("top") is not None,
            "iostat": shutil.which("iostat") is not None,
            "netstat": shutil.which("netstat") is not None,
            "ss": shutil.which("ss") is not None,
            "vmstat": shutil.which("vmstat") is not None,
            "free": shutil.which("free") is not None,
            "df": shutil.which("df") is not None,
            "lsof": shutil.which("lsof") is not None,
            "ps": shutil.which("ps") is not None
        }
        
        self.logger.info("System tools availability check", tools=tools)
        return tools
    
    async def start_monitoring(self) -> bool:
        """Start continuous system monitoring."""
        if self.is_monitoring:
            self.logger.warning("System monitoring already started")
            return False
        
        self.is_monitoring = True
        
        # Collect baseline metrics
        self.baseline_metrics = await self.collect_metrics()
        
        # Start monitoring task
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        self.logger.info("System monitoring started", 
                        interval=self.collection_interval)
        
        # Track in MCPcat (analytics disabled for this version)
        # if self.mcpcat_options:
        #     await mcpcat.track_event("system_monitoring_started", {
        #         "collection_interval": self.collection_interval,
        #         "available_tools": list(self.available_tools.keys()),
        #         "baseline_metrics": self.baseline_metrics.to_dict() if self.baseline_metrics else None
        #     })
        
        return True
    
    async def stop_monitoring(self) -> bool:
        """Stop system monitoring."""
        if not self.is_monitoring:
            return False
        
        self.is_monitoring = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        # Save final metrics
        await self._save_metrics_to_disk()
        
        self.logger.info("System monitoring stopped")
        
        # Track in MCPcat (analytics disabled for this version)
        # if self.mcpcat_options:
        #     await mcpcat.track_event("system_monitoring_stopped", {
        #         "total_snapshots": len(self.metrics_history),
        #         "monitoring_duration_seconds": (
        #             (self.metrics_history[-1].timestamp - self.metrics_history[0].timestamp).total_seconds()
        #             if len(self.metrics_history) > 1 else 0
        #         )
        #     })
        
        return True
    
    async def collect_metrics(self) -> SystemMetrics:
        """Collect current system metrics."""
        metrics = SystemMetrics()
        
        try:
            # CPU metrics
            metrics.cpu_percent = psutil.cpu_percent(interval=1)
            metrics.cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            metrics.cpu_freq = cpu_freq.current if cpu_freq else None
            metrics.load_average = list(psutil.getloadavg())
            
            # Memory metrics
            memory = psutil.virtual_memory()
            metrics.memory_total = memory.total
            metrics.memory_available = memory.available
            metrics.memory_percent = memory.percent
            metrics.memory_used = memory.used
            
            swap = psutil.swap_memory()
            metrics.swap_total = swap.total
            metrics.swap_used = swap.used
            metrics.swap_percent = swap.percent
            
            # Disk metrics
            disk_usage = psutil.disk_usage('/')
            metrics.disk_total = disk_usage.total
            metrics.disk_used = disk_usage.used
            metrics.disk_free = disk_usage.free
            metrics.disk_percent = (disk_usage.used / disk_usage.total) * 100
            
            disk_io = psutil.disk_io_counters()
            if disk_io:
                metrics.disk_io_read_bytes = disk_io.read_bytes
                metrics.disk_io_write_bytes = disk_io.write_bytes
                metrics.disk_io_read_time = disk_io.read_time
                metrics.disk_io_write_time = disk_io.write_time
            
            # Network metrics
            network_io = psutil.net_io_counters()
            if network_io:
                metrics.network_bytes_sent = network_io.bytes_sent
                metrics.network_bytes_recv = network_io.bytes_recv
                metrics.network_packets_sent = network_io.packets_sent
                metrics.network_packets_recv = network_io.packets_recv
            
            metrics.network_connections = len(psutil.net_connections())
            
            # Process-specific metrics
            metrics.process_cpu_percent = self.current_process.cpu_percent()
            
            process_memory = self.current_process.memory_info()
            metrics.process_memory_rss = process_memory.rss
            metrics.process_memory_vms = process_memory.vms
            metrics.process_memory_percent = self.current_process.memory_percent()
            
            metrics.process_num_threads = self.current_process.num_threads()
            
            try:
                metrics.process_num_fds = self.current_process.num_fds()
            except (AttributeError, psutil.AccessDenied):
                # num_fds not available on all platforms
                metrics.process_num_fds = 0
            
            try:
                metrics.process_connections = len(self.current_process.connections())
            except psutil.AccessDenied:
                metrics.process_connections = 0
            
        except Exception as e:
            self.logger.error("Failed to collect system metrics", error=str(e))
        
        return metrics
    
    async def get_top_processes(self, limit: int = 10) -> List[ProcessInfo]:
        """Get top processes by CPU usage."""
        processes = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 
                                           'memory_percent', 'num_threads', 'status', 
                                           'create_time', 'cmdline']):
                try:
                    process_info = ProcessInfo(
                        pid=proc.info['pid'],
                        name=proc.info['name'] or "Unknown",
                        cpu_percent=proc.info['cpu_percent'] or 0.0,
                        memory_rss=proc.info['memory_info'].rss if proc.info['memory_info'] else 0,
                        memory_vms=proc.info['memory_info'].vms if proc.info['memory_info'] else 0,
                        memory_percent=proc.info['memory_percent'] or 0.0,
                        num_threads=proc.info['num_threads'] or 0,
                        status=proc.info['status'] or "unknown",
                        create_time=proc.info['create_time'] or 0,
                        cmdline=proc.info['cmdline'] or []
                    )
                    processes.append(process_info)
                
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            # Sort by CPU usage and return top processes
            processes.sort(key=lambda x: x.cpu_percent, reverse=True)
            return processes[:limit]
        
        except Exception as e:
            self.logger.error("Failed to get top processes", error=str(e))
            return []
    
    async def run_system_command(self, command: str, timeout: int = 30) -> Optional[str]:
        """Run a system monitoring command and return output."""
        try:
            result = subprocess.run(
                command.split(),
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                self.logger.warning("System command failed",
                                  command=command,
                                  returncode=result.returncode,
                                  stderr=result.stderr)
                return None
        
        except subprocess.TimeoutExpired:
            self.logger.warning("System command timed out", command=command)
            return None
        except Exception as e:
            self.logger.error("Failed to run system command", 
                            command=command, error=str(e))
            return None
    
    async def get_network_connections(self) -> List[Dict[str, Any]]:
        """Get detailed network connection information."""
        connections = []
        
        try:
            for conn in psutil.net_connections(kind='inet'):
                connection_info = {
                    "fd": conn.fd,
                    "family": conn.family.name if conn.family else "unknown",
                    "type": conn.type.name if conn.type else "unknown",
                    "local_address": f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                    "remote_address": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                    "status": conn.status,
                    "pid": conn.pid
                }
                connections.append(connection_info)
        
        except psutil.AccessDenied:
            self.logger.warning("Access denied when getting network connections")
        except Exception as e:
            self.logger.error("Failed to get network connections", error=str(e))
        
        return connections
    
    async def analyze_performance_trends(self, lookback_minutes: int = 60) -> Dict[str, Any]:
        """Analyze performance trends over time."""
        if len(self.metrics_history) < 2:
            return {"error": "Insufficient data for trend analysis"}
        
        cutoff_time = datetime.now() - timedelta(minutes=lookback_minutes)
        recent_metrics = [
            m for m in self.metrics_history 
            if m.timestamp >= cutoff_time
        ]
        
        if len(recent_metrics) < 2:
            return {"error": "Insufficient recent data for trend analysis"}
        
        # Calculate trends
        cpu_trend = self._calculate_trend([m.cpu_percent for m in recent_metrics])
        memory_trend = self._calculate_trend([m.memory_percent for m in recent_metrics])
        disk_trend = self._calculate_trend([m.disk_percent for m in recent_metrics])
        
        # Process-specific trends
        process_cpu_trend = self._calculate_trend([m.process_cpu_percent for m in recent_metrics])
        process_memory_trend = self._calculate_trend([m.process_memory_percent for m in recent_metrics])
        
        # Calculate averages
        avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m.memory_percent for m in recent_metrics) / len(recent_metrics)
        avg_disk = sum(m.disk_percent for m in recent_metrics) / len(recent_metrics)
        
        # Detect anomalies
        anomalies = []
        if any(m.cpu_percent > 90 for m in recent_metrics):
            anomalies.append("High CPU usage detected")
        if any(m.memory_percent > 90 for m in recent_metrics):
            anomalies.append("High memory usage detected")
        if any(m.disk_percent > 95 for m in recent_metrics):
            anomalies.append("Low disk space detected")
        
        return {
            "analysis_period_minutes": lookback_minutes,
            "data_points": len(recent_metrics),
            "trends": {
                "cpu_percent": cpu_trend,
                "memory_percent": memory_trend,
                "disk_percent": disk_trend,
                "process_cpu_percent": process_cpu_trend,
                "process_memory_percent": process_memory_trend
            },
            "averages": {
                "cpu_percent": round(avg_cpu, 2),
                "memory_percent": round(avg_memory, 2),
                "disk_percent": round(avg_disk, 2)
            },
            "anomalies": anomalies,
            "current_metrics": recent_metrics[-1].to_dict(),
            "baseline_comparison": self._compare_to_baseline(recent_metrics[-1]) if self.baseline_metrics else None
        }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from a list of values."""
        if len(values) < 2:
            return "insufficient_data"
        
        # Simple linear trend calculation
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)
        
        diff = second_avg - first_avg
        
        if abs(diff) < 1.0:  # Less than 1% change
            return "stable"
        elif diff > 0:
            return "increasing"
        else:
            return "decreasing"
    
    def _compare_to_baseline(self, current: SystemMetrics) -> Dict[str, Any]:
        """Compare current metrics to baseline."""
        if not self.baseline_metrics:
            return {}
        
        return {
            "cpu_change": round(current.cpu_percent - self.baseline_metrics.cpu_percent, 2),
            "memory_change": round(current.memory_percent - self.baseline_metrics.memory_percent, 2),
            "disk_change": round(current.disk_percent - self.baseline_metrics.disk_percent, 2),
            "process_cpu_change": round(current.process_cpu_percent - self.baseline_metrics.process_cpu_percent, 2),
            "process_memory_change": round(current.process_memory_percent - self.baseline_metrics.process_memory_percent, 2)
        }
    
    async def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.is_monitoring:
            try:
                # Collect metrics
                metrics = await self.collect_metrics()
                self.metrics_history.append(metrics)
                
                # Limit history size
                if len(self.metrics_history) > self.max_history_size:
                    self.metrics_history = self.metrics_history[-self.max_history_size:]
                
                # Track in MCPcat (analytics disabled for this version)
                # if self.mcpcat_options:
                #     await mcpcat.track_event("system_metrics_collected", {
                #         "timestamp": metrics.timestamp.isoformat(),
                #         "cpu_percent": metrics.cpu_percent,
                #         "memory_percent": metrics.memory_percent,
                #         "disk_percent": metrics.disk_percent,
                #         "process_cpu_percent": metrics.process_cpu_percent,
                #         "process_memory_percent": metrics.process_memory_percent
                #     })
                
                # Check for alerts
                await self._check_alerts(metrics)
                
                # Wait for next collection
                await asyncio.sleep(self.collection_interval)
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("Error in monitoring loop", error=str(e))
                await asyncio.sleep(self.collection_interval)
    
    async def _check_alerts(self, metrics: SystemMetrics):
        """Check for alert conditions."""
        alerts = []
        
        # High CPU usage
        if metrics.cpu_percent > 90:
            alerts.append({
                "type": "high_cpu",
                "severity": "warning",
                "message": f"High CPU usage: {metrics.cpu_percent:.1f}%",
                "value": metrics.cpu_percent
            })
        
        # High memory usage
        if metrics.memory_percent > 90:
            alerts.append({
                "type": "high_memory",
                "severity": "warning",
                "message": f"High memory usage: {metrics.memory_percent:.1f}%",
                "value": metrics.memory_percent
            })
        
        # Low disk space
        if metrics.disk_percent > 95:
            alerts.append({
                "type": "low_disk",
                "severity": "critical",
                "message": f"Low disk space: {metrics.disk_percent:.1f}% used",
                "value": metrics.disk_percent
            })
        
        # High process CPU usage
        if metrics.process_cpu_percent > 80:
            alerts.append({
                "type": "high_process_cpu",
                "severity": "warning",
                "message": f"High process CPU usage: {metrics.process_cpu_percent:.1f}%",
                "value": metrics.process_cpu_percent
            })
        
        # Track alerts in MCPcat (analytics disabled for this version)
        # if alerts and self.mcpcat_options:
        #     for alert in alerts:
        #         await mcpcat.track_event("system_alert", alert)
        
        if alerts:
            self.logger.warning("System alerts triggered", alerts=alerts)
    
    async def _save_metrics_to_disk(self):
        """Save metrics history to disk."""
        try:
            metrics_file = self.storage_path / f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            metrics_data = {
                "collection_interval": self.collection_interval,
                "start_time": self.metrics_history[0].timestamp.isoformat() if self.metrics_history else None,
                "end_time": self.metrics_history[-1].timestamp.isoformat() if self.metrics_history else None,
                "total_snapshots": len(self.metrics_history),
                "metrics": [m.to_dict() for m in self.metrics_history]
            }
            
            with open(metrics_file, 'w') as f:
                json.dump(metrics_data, f, indent=2)
            
            self.logger.info("Metrics saved to disk", 
                           file=str(metrics_file),
                           snapshots=len(self.metrics_history))
        
        except Exception as e:
            self.logger.error("Failed to save metrics to disk", error=str(e))
    
    async def generate_system_report(self) -> Dict[str, Any]:
        """Generate comprehensive system monitoring report."""
        current_metrics = await self.collect_metrics()
        top_processes = await self.get_top_processes(10)
        network_connections = await self.get_network_connections()
        performance_trends = await self.analyze_performance_trends(60)
        
        # System information
        system_info = {
            "platform": psutil.LINUX if hasattr(psutil, 'LINUX') else "unknown",
            "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
            "uptime_seconds": time.time() - psutil.boot_time(),
            "available_tools": self.available_tools
        }
        
        return {
            "report_timestamp": datetime.now().isoformat(),
            "system_info": system_info,
            "current_metrics": current_metrics.to_dict(),
            "top_processes": [asdict(p) for p in top_processes],
            "network_connections": network_connections[:20],  # Limit to 20 connections
            "performance_trends": performance_trends,
            "monitoring_status": {
                "is_monitoring": self.is_monitoring,
                "collection_interval": self.collection_interval,
                "metrics_history_size": len(self.metrics_history),
                "baseline_available": self.baseline_metrics is not None
            }
        }