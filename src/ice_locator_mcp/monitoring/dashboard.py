"""
Monitoring Dashboard and Alerts Module.

Provides web-based dashboard for monitoring system health, user analytics,
and configurable alerting with notification systems.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field, asdict
from pathlib import Path
import logging
from enum import Enum

import structlog

from .comprehensive_monitor import ComprehensiveMonitor
from ..core.config import ServerConfig


class AlertSeverity(Enum):
    """Alert severity levels."""
    
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AlertStatus(Enum):
    """Alert status states."""
    
    ACTIVE = "active"
    RESOLVED = "resolved"
    ACKNOWLEDGED = "acknowledged"
    SUPPRESSED = "suppressed"


@dataclass
class AlertRule:
    """Configuration for an alert rule."""
    
    rule_id: str
    name: str
    description: str
    metric_name: str
    condition: str  # "gt", "lt", "eq", "ne"
    threshold: float
    severity: AlertSeverity
    enabled: bool = True
    cooldown_minutes: int = 5
    notification_channels: List[str] = field(default_factory=list)
    
    def evaluate(self, value: float) -> bool:
        """Evaluate if the alert condition is met."""
        if not self.enabled:
            return False
            
        if self.condition == "gt":
            return value > self.threshold
        elif self.condition == "lt":
            return value < self.threshold
        elif self.condition == "eq":
            return value == self.threshold
        elif self.condition == "ne":
            return value != self.threshold
        
        return False


@dataclass
class Alert:
    """Active alert instance."""
    
    alert_id: str
    rule_id: str
    title: str
    description: str
    severity: AlertSeverity
    status: AlertStatus
    triggered_at: datetime
    resolved_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    current_value: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration(self) -> timedelta:
        """Calculate alert duration."""
        end_time = self.resolved_at or datetime.now()
        return end_time - self.triggered_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary."""
        data = asdict(self)
        data["triggered_at"] = self.triggered_at.isoformat()
        data["resolved_at"] = self.resolved_at.isoformat() if self.resolved_at else None
        data["acknowledged_at"] = self.acknowledged_at.isoformat() if self.acknowledged_at else None
        data["severity"] = self.severity.value
        data["status"] = self.status.value
        data["duration_seconds"] = int(self.duration.total_seconds())
        return data


class NotificationChannel:
    """Base class for notification channels."""
    
    def __init__(self, channel_id: str, config: Dict[str, Any]):
        self.channel_id = channel_id
        self.config = config
        self.logger = structlog.get_logger(__name__)
    
    async def send_notification(self, alert: Alert) -> bool:
        """Send notification for an alert."""
        raise NotImplementedError


class LogNotificationChannel(NotificationChannel):
    """Log-based notification channel."""
    
    async def send_notification(self, alert: Alert) -> bool:
        """Send notification via logging."""
        try:
            self.logger.warning(
                "ALERT NOTIFICATION",
                alert_id=alert.alert_id,
                title=alert.title,
                severity=alert.severity.value,
                current_value=alert.current_value,
                description=alert.description
            )
            return True
        except Exception as e:
            self.logger.error("Failed to send log notification", error=str(e))
            return False


class WebhookNotificationChannel(NotificationChannel):
    """Webhook-based notification channel."""
    
    async def send_notification(self, alert: Alert) -> bool:
        """Send notification via webhook."""
        try:
            import httpx
            
            webhook_url = self.config.get("url")
            if not webhook_url:
                self.logger.error("Webhook URL not configured")
                return False
            
            payload = {
                "alert": alert.to_dict(),
                "timestamp": datetime.now().isoformat(),
                "source": "ice-locator-mcp"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    webhook_url,
                    json=payload,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    self.logger.info("Webhook notification sent", alert_id=alert.alert_id)
                    return True
                else:
                    self.logger.error("Webhook notification failed", 
                                    status_code=response.status_code,
                                    response=response.text)
                    return False
                    
        except Exception as e:
            self.logger.error("Failed to send webhook notification", error=str(e))
            return False


class EmailNotificationChannel(NotificationChannel):
    """Email-based notification channel."""
    
    async def send_notification(self, alert: Alert) -> bool:
        """Send notification via email."""
        try:
            # Note: This would require email configuration
            # For now, just log the email that would be sent
            self.logger.info(
                "EMAIL NOTIFICATION (simulated)",
                alert_id=alert.alert_id,
                to=self.config.get("recipients", []),
                subject=f"[{alert.severity.value.upper()}] {alert.title}",
                body=alert.description
            )
            return True
        except Exception as e:
            self.logger.error("Failed to send email notification", error=str(e))
            return False


class AlertManager:
    """Manages alert rules, active alerts, and notifications."""
    
    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize alert manager."""
        self.logger = structlog.get_logger(__name__)
        
        # Storage
        self.storage_path = storage_path or Path.home() / ".cache" / "ice-locator-mcp" / "alerts"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Alert state
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        
        # Notification channels
        self.notification_channels: Dict[str, NotificationChannel] = {}
        
        # Cooldown tracking
        self.rule_cooldowns: Dict[str, datetime] = {}
        
        # Initialize default alert rules
        self._initialize_default_rules()
        
        # Initialize default notification channels
        self._initialize_default_channels()
        
        self.logger.info("Alert manager initialized", 
                        storage_path=str(self.storage_path))
    
    def _initialize_default_rules(self):
        """Initialize default alert rules."""
        default_rules = [
            AlertRule(
                rule_id="high_cpu",
                name="High CPU Usage",
                description="CPU usage is above 90%",
                metric_name="cpu_percent",
                condition="gt",
                threshold=90.0,
                severity=AlertSeverity.WARNING,
                cooldown_minutes=5,
                notification_channels=["log", "webhook"]
            ),
            AlertRule(
                rule_id="high_memory",
                name="High Memory Usage",
                description="Memory usage is above 90%",
                metric_name="memory_percent",
                condition="gt",
                threshold=90.0,
                severity=AlertSeverity.WARNING,
                cooldown_minutes=5,
                notification_channels=["log", "webhook"]
            ),
            AlertRule(
                rule_id="low_disk",
                name="Low Disk Space",
                description="Disk usage is above 95%",
                metric_name="disk_percent",
                condition="gt",
                threshold=95.0,
                severity=AlertSeverity.CRITICAL,
                cooldown_minutes=10,
                notification_channels=["log", "webhook", "email"]
            ),
            AlertRule(
                rule_id="high_error_rate",
                name="High Error Rate",
                description="Tool error rate is above 50%",
                metric_name="error_rate_percent",
                condition="gt",
                threshold=50.0,
                severity=AlertSeverity.WARNING,
                cooldown_minutes=3,
                notification_channels=["log", "webhook"]
            ),
            AlertRule(
                rule_id="process_high_cpu",
                name="Process High CPU",
                description="Process CPU usage is above 80%",
                metric_name="process_cpu_percent",
                condition="gt",
                threshold=80.0,
                severity=AlertSeverity.WARNING,
                cooldown_minutes=5,
                notification_channels=["log"]
            )
        ]
        
        for rule in default_rules:
            self.alert_rules[rule.rule_id] = rule
    
    def _initialize_default_channels(self):
        """Initialize default notification channels."""
        # Log channel (always available)
        self.notification_channels["log"] = LogNotificationChannel("log", {})
        
        # Webhook channel (configure via environment)
        webhook_url = None  # Could be loaded from config
        if webhook_url:
            self.notification_channels["webhook"] = WebhookNotificationChannel(
                "webhook", {"url": webhook_url}
            )
        
        # Email channel (configure via environment)
        email_recipients = []  # Could be loaded from config
        if email_recipients:
            self.notification_channels["email"] = EmailNotificationChannel(
                "email", {"recipients": email_recipients}
            )
    
    async def evaluate_metrics(self, metrics: Dict[str, float]):
        """Evaluate metrics against alert rules."""
        for rule_id, rule in self.alert_rules.items():
            if not rule.enabled:
                continue
            
            # Check cooldown
            if rule_id in self.rule_cooldowns:
                cooldown_end = self.rule_cooldowns[rule_id] + timedelta(minutes=rule.cooldown_minutes)
                if datetime.now() < cooldown_end:
                    continue
            
            # Get metric value
            metric_value = metrics.get(rule.metric_name)
            if metric_value is None:
                continue
            
            # Evaluate rule
            is_triggered = rule.evaluate(metric_value)
            
            if is_triggered:
                await self._trigger_alert(rule, metric_value)
            else:
                # Check if we should resolve an existing alert
                existing_alert = self.active_alerts.get(rule_id)
                if existing_alert and existing_alert.status == AlertStatus.ACTIVE:
                    await self._resolve_alert(rule_id)
    
    async def _trigger_alert(self, rule: AlertRule, current_value: float):
        """Trigger a new alert."""
        # Check if alert is already active
        if rule.rule_id in self.active_alerts:
            existing_alert = self.active_alerts[rule.rule_id]
            if existing_alert.status == AlertStatus.ACTIVE:
                # Update current value but don't create new alert
                existing_alert.current_value = current_value
                return
        
        # Create new alert
        alert = Alert(
            alert_id=f"{rule.rule_id}_{int(datetime.now().timestamp())}",
            rule_id=rule.rule_id,
            title=rule.name,
            description=f"{rule.description} (Current: {current_value})",
            severity=rule.severity,
            status=AlertStatus.ACTIVE,
            triggered_at=datetime.now(),
            current_value=current_value
        )
        
        # Store alert
        self.active_alerts[rule.rule_id] = alert
        self.alert_history.append(alert)
        
        # Set cooldown
        self.rule_cooldowns[rule.rule_id] = datetime.now()
        
        # Send notifications
        await self._send_notifications(alert, rule.notification_channels)
        
        self.logger.warning("Alert triggered",
                          alert_id=alert.alert_id,
                          rule_id=rule.rule_id,
                          severity=rule.severity.value,
                          current_value=current_value)
    
    async def _resolve_alert(self, rule_id: str):
        """Resolve an active alert."""
        alert = self.active_alerts.get(rule_id)
        if not alert:
            return
        
        alert.status = AlertStatus.RESOLVED
        alert.resolved_at = datetime.now()
        
        # Remove from active alerts
        del self.active_alerts[rule_id]
        
        self.logger.info("Alert resolved",
                        alert_id=alert.alert_id,
                        rule_id=rule_id,
                        duration=str(alert.duration))
    
    async def _send_notifications(self, alert: Alert, channel_names: List[str]):
        """Send notifications through specified channels."""
        for channel_name in channel_names:
            channel = self.notification_channels.get(channel_name)
            if channel:
                try:
                    success = await channel.send_notification(alert)
                    if success:
                        self.logger.debug("Notification sent",
                                        alert_id=alert.alert_id,
                                        channel=channel_name)
                    else:
                        self.logger.error("Notification failed",
                                        alert_id=alert.alert_id,
                                        channel=channel_name)
                except Exception as e:
                    self.logger.error("Notification error",
                                    alert_id=alert.alert_id,
                                    channel=channel_name,
                                    error=str(e))
    
    async def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert."""
        for alert in self.active_alerts.values():
            if alert.alert_id == alert_id:
                alert.status = AlertStatus.ACKNOWLEDGED
                alert.acknowledged_at = datetime.now()
                self.logger.info("Alert acknowledged", alert_id=alert_id)
                return True
        return False
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get all active alerts."""
        return [alert.to_dict() for alert in self.active_alerts.values()]
    
    def get_alert_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get alert history."""
        recent_alerts = sorted(self.alert_history, key=lambda x: x.triggered_at, reverse=True)
        return [alert.to_dict() for alert in recent_alerts[:limit]]
    
    def get_alert_rules(self) -> List[Dict[str, Any]]:
        """Get all alert rules."""
        return [asdict(rule) for rule in self.alert_rules.values()]
    
    def update_alert_rule(self, rule_id: str, updates: Dict[str, Any]) -> bool:
        """Update an alert rule."""
        rule = self.alert_rules.get(rule_id)
        if not rule:
            return False
        
        for key, value in updates.items():
            if hasattr(rule, key):
                setattr(rule, key, value)
        
        self.logger.info("Alert rule updated", rule_id=rule_id, updates=updates)
        return True


class MonitoringDashboard:
    """Web dashboard for monitoring and alerts."""
    
    def __init__(self, comprehensive_monitor: ComprehensiveMonitor,
                 alert_manager: AlertManager,
                 config: ServerConfig):
        """Initialize monitoring dashboard."""
        self.logger = structlog.get_logger(__name__)
        self.comprehensive_monitor = comprehensive_monitor
        self.alert_manager = alert_manager
        self.config = config
        
        # Dashboard state
        self.is_running = False
        self.dashboard_task: Optional[asyncio.Task] = None
        
        # Metrics cache
        self.cached_metrics: Dict[str, Any] = {}
        self.cache_timestamp: Optional[datetime] = None
        self.cache_ttl_seconds = 30
        
        self.logger.info("Monitoring dashboard initialized")
    
    async def start_dashboard(self, port: int = 8080) -> bool:
        """Start the monitoring dashboard web server."""
        if self.is_running:
            self.logger.warning("Dashboard already running")
            return False
        
        try:
            # For now, just start the monitoring loop
            # In a full implementation, this would start a web server
            self.is_running = True
            self.dashboard_task = asyncio.create_task(self._monitoring_loop())
            
            self.logger.info("Monitoring dashboard started", port=port)
            return True
            
        except Exception as e:
            self.logger.error("Failed to start dashboard", error=str(e))
            return False
    
    async def stop_dashboard(self) -> bool:
        """Stop the monitoring dashboard."""
        if not self.is_running:
            return False
        
        self.is_running = False
        
        if self.dashboard_task:
            self.dashboard_task.cancel()
            try:
                await self.dashboard_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Monitoring dashboard stopped")
        return True
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data."""
        # Check cache
        if (self.cache_timestamp and 
            datetime.now() - self.cache_timestamp < timedelta(seconds=self.cache_ttl_seconds)):
            return self.cached_metrics
        
        try:
            # Get fresh data
            dashboard_data = await self.comprehensive_monitor.generate_analytics_dashboard_data(7)
            
            # Add alert information
            dashboard_data["alerts"] = {
                "active_alerts": self.alert_manager.get_active_alerts(),
                "alert_history": self.alert_manager.get_alert_history(50),
                "alert_rules": self.alert_manager.get_alert_rules()
            }
            
            # Add system status
            dashboard_data["system_status"] = await self.comprehensive_monitor.get_health_status()
            
            # Cache the data
            self.cached_metrics = dashboard_data
            self.cache_timestamp = datetime.now()
            
            return dashboard_data
            
        except Exception as e:
            self.logger.error("Failed to get dashboard data", error=str(e))
            return {"error": str(e)}
    
    async def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get real-time system metrics."""
        try:
            if self.comprehensive_monitor.system_monitor:
                current_metrics = await self.comprehensive_monitor.system_monitor.collect_metrics()
                return current_metrics.to_dict()
            else:
                return {"error": "System monitor not available"}
        except Exception as e:
            self.logger.error("Failed to get real-time metrics", error=str(e))
            return {"error": str(e)}
    
    async def _monitoring_loop(self):
        """Main monitoring loop for dashboard."""
        while self.is_running:
            try:
                # Get current metrics
                if self.comprehensive_monitor.system_monitor:
                    metrics = await self.comprehensive_monitor.system_monitor.collect_metrics()
                    
                    # Convert to flat metrics dict for alert evaluation
                    flat_metrics = {
                        "cpu_percent": metrics.cpu_percent,
                        "memory_percent": metrics.memory_percent,
                        "disk_percent": metrics.disk_percent,
                        "process_cpu_percent": metrics.process_cpu_percent,
                        "process_memory_percent": metrics.process_memory_percent
                    }
                    
                    # Add derived metrics
                    # Note: Error rate would need to be calculated from session data
                    flat_metrics["error_rate_percent"] = 0.0  # Placeholder
                    
                    # Evaluate alerts
                    await self.alert_manager.evaluate_metrics(flat_metrics)
                
                # Wait before next iteration
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("Error in monitoring loop", error=str(e))
                await asyncio.sleep(30)
    
    def generate_dashboard_html(self, data: Dict[str, Any]) -> str:
        """Generate basic HTML dashboard (for demonstration)."""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>ICE Locator MCP - Monitoring Dashboard</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .metric {{ background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 5px; }}
                .alert {{ padding: 10px; margin: 10px 0; border-radius: 5px; }}
                .alert.warning {{ background: #fff3cd; border: 1px solid #ffeaa7; }}
                .alert.critical {{ background: #f8d7da; border: 1px solid #f5c6cb; }}
                .healthy {{ color: green; }}
                .degraded {{ color: orange; }}
                .critical {{ color: red; }}
            </style>
        </head>
        <body>
            <h1>ICE Locator MCP - Monitoring Dashboard</h1>
            
            <h2>System Health: <span class="{data.get('health_status', {}).get('overall_status', 'unknown')}">{data.get('health_status', {}).get('overall_status', 'Unknown').upper()}</span></h2>
            
            <h3>Active Alerts ({len(data.get('alerts', {}).get('active_alerts', []))})</h3>
            <div id="alerts">
        """
        
        # Add active alerts
        for alert in data.get('alerts', {}).get('active_alerts', []):
            html += f"""
                <div class="alert {alert['severity']}">
                    <strong>{alert['title']}</strong> - {alert['description']}<br>
                    <small>Triggered: {alert['triggered_at']} | Duration: {alert['duration_seconds']}s</small>
                </div>
            """
        
        if not data.get('alerts', {}).get('active_alerts'):
            html += "<p>No active alerts</p>"
        
        # Add system metrics
        health_status = data.get('health_status', {})
        system_component = health_status.get('components', {}).get('system', {})
        
        html += f"""
            </div>
            
            <h3>System Metrics</h3>
            <div class="metric">CPU Usage: {system_component.get('cpu_percent', 'N/A')}%</div>
            <div class="metric">Memory Usage: {system_component.get('memory_percent', 'N/A')}%</div>
            <div class="metric">Disk Usage: {system_component.get('disk_percent', 'N/A')}%</div>
            
            <h3>Analytics Summary</h3>
            <div class="metric">Total Sessions: {data.get('analytics_summary', {}).get('total_sessions', 'N/A')}</div>
            <div class="metric">Total Tool Calls: {data.get('analytics_summary', {}).get('total_tool_calls', 'N/A')}</div>
            <div class="metric">Average Session Duration: {data.get('analytics_summary', {}).get('average_session_duration_seconds', 'N/A')}s</div>
            
            <small>Generated at: {data.get('generated_at', 'Unknown')}</small>
        </body>
        </html>
        """
        
        return html