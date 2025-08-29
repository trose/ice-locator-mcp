"""
Comprehensive Monitoring Integration Module.

Combines MCPcat analytics, telemetry framework, user analytics, session replay,
and system monitoring into a unified monitoring solution.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

import structlog

from .telemetry_exporters import TelemetryExporter, TelemetryConfig
from .user_analytics import UserAnalytics
from .session_replay import SessionRecorder
from .system_monitor import SystemMonitor
from ..core.config import MonitoringConfig


class ComprehensiveMonitor:
    """Unified monitoring system combining all monitoring components."""
    
    def __init__(self, config: MonitoringConfig,
                 storage_path: Optional[Path] = None):
        """Initialize comprehensive monitoring system."""
        self.logger = structlog.get_logger(__name__)
        self.config = config
        
        # Storage configuration
        self.storage_path = storage_path or Path.home() / ".cache" / "ice-locator-mcp" / "monitoring"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.mcpcat_monitor: Optional[Any] = None
        self.telemetry_exporter: Optional[TelemetryExporter] = None
        self.user_analytics: Optional[UserAnalytics] = None
        self.session_recorder: Optional[SessionRecorder] = None
        self.system_monitor: Optional[SystemMonitor] = None
        
        # Monitoring state
        self.is_initialized = False
        self.is_monitoring = False
        
        # Aggregated metrics
        self.session_metrics: Dict[str, Any] = {}
        self.system_health_status = "unknown"
        
        self.logger.info("Comprehensive monitor created",
                        mcpcat_enabled=config.mcpcat_enabled,
                        privacy_level=config.redaction_level,
                        storage_path=str(self.storage_path))
    
    async def initialize(self) -> bool:
        """Initialize all monitoring components."""
        try:
            # Initialize MCPcat if enabled
            if self.config.mcpcat_enabled:
                from .mcpcat_integration import MCPcatMonitor, MCPcatConfig
                
                mcpcat_config = MCPcatConfig(
                    enabled=self.config.mcpcat_enabled,
                    project_id="proj_31wD5K62DcuF4XH65PCrsyv7MIO",  # Default project ID
                    redaction_level=self.config.redaction_level,
                    identify_users=self.config.identify_users
                )
                
                self.mcpcat_monitor = MCPcatMonitor(
                    mcpcat_config,
                    telemetry_exporter=None  # Will be set after telemetry initialization
                )
            
            # Initialize telemetry framework
            if self.config.mcpcat_enabled:
                telemetry_config = TelemetryConfig.from_env()
                self.telemetry_exporter = TelemetryExporter(telemetry_config)
                await self.telemetry_exporter.initialize()
                
                # Link telemetry to MCPcat monitor
                if self.mcpcat_monitor:
                    self.mcpcat_monitor.telemetry_exporter = self.telemetry_exporter
            
            # Initialize user analytics
            self.user_analytics = UserAnalytics(
                mcpcat_client=self.mcpcat_client,
                storage_path=self.storage_path / "analytics"
            )
            
            # Initialize session recorder with privacy controls
            privacy_level = "strict" if self.config.redaction_level == "strict" else "standard"
            self.session_recorder = SessionRecorder(
                storage_path=self.storage_path / "replays",
                privacy_level=privacy_level
            )
            
            # Initialize system monitor
            self.system_monitor = SystemMonitor(
                mcpcat_client=self.mcpcat_client,
                collection_interval=30,  # Collect every 30 seconds
                storage_path=self.storage_path / "system"
            )
            
            self.is_initialized = True
            
            self.logger.info("Comprehensive monitoring initialized successfully",
                           components_initialized=[
                               "mcpcat" if self.mcpcat_monitor else None,
                               "telemetry" if self.telemetry_exporter else None,
                               "analytics" if self.user_analytics else None,
                               "session_replay" if self.session_recorder else None,
                               "system_monitor" if self.system_monitor else None
                           ])
            
            return True
            
        except Exception as e:
            self.logger.error("Failed to initialize comprehensive monitoring", error=str(e))
            return False
    
    async def start_monitoring(self, session_metadata: Optional[Dict[str, Any]] = None) -> str:
        """Start comprehensive monitoring for a new session."""
        if not self.is_initialized:
            await self.initialize()
        
        if self.is_monitoring:
            self.logger.warning("Monitoring already started")
            return ""
        
        try:
            # Generate session ID
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{id(self)}"
            
            # Start user analytics session
            if self.user_analytics:
                await self.user_analytics.create_session(session_metadata)
            
            # Start session recording
            if self.session_recorder:
                await self.session_recorder.start_recording(session_id, session_metadata)
            
            # Start system monitoring
            if self.system_monitor:
                await self.system_monitor.start_monitoring()
            
            self.is_monitoring = True
            
            self.logger.info("Comprehensive monitoring started", 
                           session_id=session_id,
                           metadata=session_metadata)
            
            # Track monitoring start
            if self.mcpcat_client:
                await self.mcpcat_client.track_event("comprehensive_monitoring_started", {
                    "session_id": session_id,
                    "components": [
                        "mcpcat", "telemetry", "analytics", "session_replay", "system_monitor"
                    ],
                    "metadata": session_metadata
                })
            
            return session_id
            
        except Exception as e:
            self.logger.error("Failed to start comprehensive monitoring", error=str(e))
            return ""
    
    async def stop_monitoring(self, session_id: str) -> bool:
        """Stop comprehensive monitoring."""
        if not self.is_monitoring:
            return False
        
        try:
            # Stop user analytics session
            if self.user_analytics:
                await self.user_analytics.end_session(session_id)
            
            # Stop session recording
            if self.session_recorder:
                await self.session_recorder.stop_recording(session_id)
            
            # Stop system monitoring
            if self.system_monitor:
                await self.system_monitor.stop_monitoring()
            
            self.is_monitoring = False
            
            # Generate final session report
            session_report = await self.generate_session_report(session_id)
            
            self.logger.info("Comprehensive monitoring stopped", 
                           session_id=session_id,
                           session_summary=session_report.get("summary", {}))
            
            # Track monitoring stop
            if self.mcpcat_client:
                await self.mcpcat_client.track_event("comprehensive_monitoring_stopped", {
                    "session_id": session_id,
                    "session_report": session_report
                })
            
            return True
            
        except Exception as e:
            self.logger.error("Failed to stop comprehensive monitoring", error=str(e))
            return False
    
    async def track_tool_call(self, session_id: str, tool_name: str,
                             arguments: Dict[str, Any], 
                             result: Optional[Dict[str, Any]] = None,
                             error: Optional[str] = None,
                             duration_ms: Optional[int] = None):
        """Track a tool call across all monitoring systems."""
        try:
            # Track in MCPcat
            if self.mcpcat_monitor:
                await self.mcpcat_monitor.track_tool_call(tool_name, arguments)
                if result or error:
                    if error:
                        await self.mcpcat_monitor.track_tool_error(tool_name, error)
                    else:
                        await self.mcpcat_monitor.track_tool_success(tool_name, result)
            
            # Track in user analytics
            if self.user_analytics:
                await self.user_analytics.track_tool_call(
                    session_id, tool_name, arguments, result, error, duration_ms
                )
            
            # Record in session replay
            if self.session_recorder:
                await self.session_recorder.record_tool_call(
                    session_id, tool_name, arguments, result, error, duration_ms
                )
            
            # Update session metrics
            self._update_session_metrics(tool_name, error is None, duration_ms)
            
        except Exception as e:
            self.logger.error("Failed to track tool call", 
                            session_id=session_id, tool_name=tool_name, error=str(e))
    
    async def track_error(self, session_id: str, error_type: str, 
                         error_message: str, context: Optional[Dict[str, Any]] = None):
        """Track an error across all monitoring systems."""
        try:
            # Record in session replay
            if self.session_recorder:
                await self.session_recorder.record_error(
                    session_id, error_type, error_message, context=context
                )
            
            # Track in telemetry
            if self.telemetry_exporter:
                await self.telemetry_exporter.record_error(error_type, error_message, context)
            
            # Track in MCPcat
            if self.mcpcat_client:
                await self.mcpcat_client.track_event("error_occurred", {
                    "session_id": session_id,
                    "error_type": error_type,
                    "error_message": error_message,
                    "context": context
                })
            
        except Exception as e:
            self.logger.error("Failed to track error", 
                            session_id=session_id, error=str(e))
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status across all monitoring systems."""
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "components": {}
        }
        
        try:
            # System monitor health
            if self.system_monitor:
                system_metrics = await self.system_monitor.collect_metrics()
                health_status["components"]["system"] = {
                    "status": "healthy" if system_metrics.cpu_percent < 80 and 
                             system_metrics.memory_percent < 80 else "degraded",
                    "cpu_percent": system_metrics.cpu_percent,
                    "memory_percent": system_metrics.memory_percent,
                    "disk_percent": system_metrics.disk_percent
                }
            
            # MCPcat connection health
            if self.mcpcat_monitor:
                health_status["components"]["mcpcat"] = {
                    "status": "healthy",  # Assume healthy if initialized
                    "project_id": self.config.mcpcat_project_id,
                    "local_only": self.config.local_only
                }
            
            # Telemetry health
            if self.telemetry_exporter:
                health_status["components"]["telemetry"] = {
                    "status": "healthy",
                    "exporters": list(self.telemetry_exporter.config.exporters.keys())
                }
            
            # User analytics health
            if self.user_analytics:
                active_sessions = len(self.user_analytics.active_sessions)
                health_status["components"]["analytics"] = {
                    "status": "healthy",
                    "active_sessions": active_sessions
                }
            
            # Session recorder health
            if self.session_recorder:
                active_recordings = len(self.session_recorder.active_replays)
                health_status["components"]["session_replay"] = {
                    "status": "healthy",
                    "active_recordings": active_recordings
                }
            
            # Determine overall status
            component_statuses = [
                comp.get("status", "unknown") 
                for comp in health_status["components"].values()
            ]
            
            if "critical" in component_statuses:
                health_status["overall_status"] = "critical"
            elif "degraded" in component_statuses:
                health_status["overall_status"] = "degraded"
            else:
                health_status["overall_status"] = "healthy"
            
            self.system_health_status = health_status["overall_status"]
            
        except Exception as e:
            self.logger.error("Failed to get health status", error=str(e))
            health_status["overall_status"] = "error"
            health_status["error"] = str(e)
        
        return health_status
    
    async def generate_session_report(self, session_id: str) -> Dict[str, Any]:
        """Generate comprehensive session report."""
        report = {
            "session_id": session_id,
            "generated_at": datetime.now().isoformat(),
            "summary": {},
            "analytics": {},
            "system_metrics": {},
            "session_replay": {},
            "telemetry": {}
        }
        
        try:
            # Get analytics data
            if self.user_analytics:
                analytics_data = await self.user_analytics.get_session_analytics(session_id)
                if analytics_data:
                    report["analytics"] = analytics_data
                    report["summary"]["tool_calls"] = analytics_data.get("tool_calls", 0)
                    report["summary"]["duration"] = analytics_data.get("duration", "unknown")
            
            # Get system metrics summary
            if self.system_monitor:
                system_report = await self.system_monitor.generate_system_report()
                report["system_metrics"] = {
                    "current_metrics": system_report.get("current_metrics", {}),
                    "performance_trends": system_report.get("performance_trends", {}),
                    "monitoring_status": system_report.get("monitoring_status", {})
                }
            
            # Get session replay summary
            if self.session_recorder:
                replay_summary = await self.session_recorder.get_replay_summary(session_id)
                if replay_summary:
                    report["session_replay"] = replay_summary
                    report["summary"]["events"] = replay_summary.get("total_events", 0)
                    report["summary"]["errors"] = len(replay_summary.get("errors", []))
            
            # Add telemetry summary
            if self.telemetry_exporter:
                report["telemetry"] = {
                    "exporters_configured": list(self.telemetry_exporter.config.exporters.keys()),
                    "spans_recorded": "N/A",  # Would need span counter
                    "metrics_recorded": "N/A"  # Would need metrics counter
                }
            
            # Calculate overall session quality score
            report["summary"]["quality_score"] = self._calculate_session_quality_score(report)
            
        except Exception as e:
            self.logger.error("Failed to generate session report", 
                            session_id=session_id, error=str(e))
            report["error"] = str(e)
        
        return report
    
    async def generate_analytics_dashboard_data(self, days: int = 7) -> Dict[str, Any]:
        """Generate data for monitoring dashboard."""
        dashboard_data = {
            "generated_at": datetime.now().isoformat(),
            "period_days": days,
            "health_status": await self.get_health_status(),
            "analytics_summary": {},
            "system_summary": {},
            "session_patterns": {},
            "performance_metrics": {}
        }
        
        try:
            # Get analytics summary
            if self.user_analytics:
                analytics_report = await self.user_analytics.generate_analytics_report(days)
                dashboard_data["analytics_summary"] = analytics_report
            
            # Get system performance trends
            if self.system_monitor:
                performance_trends = await self.system_monitor.analyze_performance_trends(days * 24 * 60)
                dashboard_data["performance_metrics"] = performance_trends
            
            # Get session patterns
            dashboard_data["session_patterns"] = self._analyze_session_patterns()
            
        except Exception as e:
            self.logger.error("Failed to generate dashboard data", error=str(e))
            dashboard_data["error"] = str(e)
        
        return dashboard_data
    
    def _update_session_metrics(self, tool_name: str, success: bool, duration_ms: Optional[int]):
        """Update internal session metrics."""
        if "tool_calls" not in self.session_metrics:
            self.session_metrics["tool_calls"] = {}
            self.session_metrics["success_rate"] = {"successful": 0, "failed": 0}
            self.session_metrics["average_duration"] = {"total_ms": 0, "count": 0}
        
        # Update tool call count
        self.session_metrics["tool_calls"][tool_name] = self.session_metrics["tool_calls"].get(tool_name, 0) + 1
        
        # Update success rate
        if success:
            self.session_metrics["success_rate"]["successful"] += 1
        else:
            self.session_metrics["success_rate"]["failed"] += 1
        
        # Update duration metrics
        if duration_ms:
            self.session_metrics["average_duration"]["total_ms"] += duration_ms
            self.session_metrics["average_duration"]["count"] += 1
    
    def _calculate_session_quality_score(self, report: Dict[str, Any]) -> float:
        """Calculate a quality score for the session (0-100)."""
        score = 100.0
        
        try:
            # Deduct points for errors
            errors = report.get("session_replay", {}).get("errors", [])
            score -= len(errors) * 10  # 10 points per error
            
            # Deduct points for poor performance
            system_metrics = report.get("system_metrics", {}).get("current_metrics", {})
            if system_metrics.get("cpu_percent", 0) > 80:
                score -= 20
            if system_metrics.get("memory_percent", 0) > 80:
                score -= 20
            
            # Add points for successful tool calls
            tool_calls = report.get("analytics", {}).get("tool_calls", 0)
            if tool_calls > 0:
                score += min(tool_calls * 2, 20)  # Max 20 points for tool usage
            
            # Ensure score is within bounds
            score = max(0, min(100, score))
            
        except Exception:
            score = 50.0  # Default score if calculation fails
        
        return round(score, 1)
    
    def _analyze_session_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in session data."""
        return {
            "most_used_tools": {},
            "peak_usage_hours": [],
            "average_session_length": "unknown",
            "common_error_patterns": [],
            "user_behavior_insights": []
        }
    
    async def cleanup(self):
        """Cleanup all monitoring resources."""
        try:
            if self.is_monitoring:
                await self.stop_monitoring("cleanup")
            
            # Cleanup individual components
            if self.mcpcat_monitor:
                await self.mcpcat_monitor.cleanup()
            
            if self.telemetry_exporter:
                await self.telemetry_exporter.cleanup()
            
            if self.user_analytics:
                await self.user_analytics.cleanup_old_data()
            
            if self.session_recorder:
                await self.session_recorder.cleanup_old_replays()
            
            self.logger.info("Comprehensive monitoring cleanup completed")
            
        except Exception as e:
            self.logger.error("Failed to cleanup monitoring", error=str(e))