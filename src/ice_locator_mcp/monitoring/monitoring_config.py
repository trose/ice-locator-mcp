"""
Centralized monitoring configuration management.

Combines MCPcat, telemetry, and OS monitoring configurations
into a unified configuration system.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from pathlib import Path

from .mcpcat_integration import MCPcatConfig
from .telemetry_exporters import TelemetryConfig


@dataclass
class OSMonitoringConfig:
    """Configuration for OS-level monitoring."""
    
    enabled: bool = True
    collection_interval: int = 60  # seconds
    metrics_to_collect: list = field(default_factory=lambda: [
        "cpu_percent",
        "memory_percent", 
        "disk_usage",
        "network_io",
        "process_count"
    ])
    process_monitoring: bool = True
    network_monitoring: bool = True
    
    @classmethod
    def from_env(cls) -> "OSMonitoringConfig":
        """Create OS monitoring configuration from environment variables."""
        return cls(
            enabled=os.getenv("ICE_LOCATOR_OS_MONITORING_ENABLED", "true").lower() == "true",
            collection_interval=int(os.getenv("ICE_LOCATOR_OS_MONITORING_INTERVAL", "60")),
            process_monitoring=os.getenv("ICE_LOCATOR_PROCESS_MONITORING", "true").lower() == "true",
            network_monitoring=os.getenv("ICE_LOCATOR_NETWORK_MONITORING", "true").lower() == "true"
        )


@dataclass
class DashboardConfig:
    """Configuration for monitoring dashboard."""
    
    enabled: bool = True
    port: int = 8080
    host: str = "localhost"
    refresh_interval: int = 30  # seconds
    include_sensitive_data: bool = False  # Privacy protection
    
    @classmethod
    def from_env(cls) -> "DashboardConfig":
        """Create dashboard configuration from environment variables."""
        return cls(
            enabled=os.getenv("ICE_LOCATOR_DASHBOARD_ENABLED", "true").lower() == "true",
            port=int(os.getenv("ICE_LOCATOR_DASHBOARD_PORT", "8080")),
            host=os.getenv("ICE_LOCATOR_DASHBOARD_HOST", "localhost"),
            refresh_interval=int(os.getenv("ICE_LOCATOR_DASHBOARD_REFRESH", "30")),
            include_sensitive_data=os.getenv("ICE_LOCATOR_DASHBOARD_SENSITIVE", "false").lower() == "true"
        )


@dataclass
class AlertingConfig:
    """Configuration for alerting and notifications."""
    
    enabled: bool = True
    alert_channels: list = field(default_factory=list)
    thresholds: Dict[str, float] = field(default_factory=lambda: {
        "cpu_percent": 80.0,
        "memory_percent": 85.0,
        "error_rate": 5.0,
        "response_time": 5000.0  # milliseconds
    })
    cooldown_period: int = 300  # seconds
    
    @classmethod
    def from_env(cls) -> "AlertingConfig":
        """Create alerting configuration from environment variables."""
        
        # Parse alert channels from environment
        channels = []
        if os.getenv("SLACK_WEBHOOK_URL"):
            channels.append({
                "type": "slack",
                "webhook_url": os.getenv("SLACK_WEBHOOK_URL"),
                "channel": os.getenv("SLACK_CHANNEL", "#alerts")
            })
        
        if os.getenv("PAGERDUTY_API_KEY"):
            channels.append({
                "type": "pagerduty",
                "api_key": os.getenv("PAGERDUTY_API_KEY"),
                "service_key": os.getenv("PAGERDUTY_SERVICE_KEY")
            })
        
        if os.getenv("EMAIL_SMTP_HOST"):
            channels.append({
                "type": "email",
                "smtp_host": os.getenv("EMAIL_SMTP_HOST"),
                "smtp_port": int(os.getenv("EMAIL_SMTP_PORT", "587")),
                "username": os.getenv("EMAIL_USERNAME"),
                "password": os.getenv("EMAIL_PASSWORD"),
                "to_addresses": os.getenv("EMAIL_ALERT_TO", "").split(",")
            })
        
        return cls(
            enabled=os.getenv("ICE_LOCATOR_ALERTING_ENABLED", "true").lower() == "true",
            alert_channels=channels,
            cooldown_period=int(os.getenv("ICE_LOCATOR_ALERT_COOLDOWN", "300"))
        )


@dataclass
class MonitoringConfig:
    """Unified monitoring configuration."""
    
    # Sub-configurations
    mcpcat: MCPcatConfig = field(default_factory=MCPcatConfig)
    telemetry: TelemetryConfig = field(default_factory=TelemetryConfig)
    os_monitoring: OSMonitoringConfig = field(default_factory=OSMonitoringConfig)
    dashboard: DashboardConfig = field(default_factory=DashboardConfig)
    alerting: AlertingConfig = field(default_factory=AlertingConfig)
    
    # Global settings
    enabled: bool = True
    privacy_mode: str = "strict"  # strict, moderate, disabled
    data_retention_days: int = 30
    export_logs_to_file: bool = True
    log_file_path: Optional[Path] = None
    
    def __post_init__(self):
        """Post-initialization setup."""
        if self.log_file_path is None:
            self.log_file_path = Path.home() / ".logs" / "ice-locator-mcp" / "monitoring.log"
    
    @classmethod
    def from_env(cls) -> "MonitoringConfig":
        """Create complete monitoring configuration from environment variables."""
        
        return cls(
            mcpcat=MCPcatConfig.from_env(),
            telemetry=TelemetryConfig.from_env(),
            os_monitoring=OSMonitoringConfig.from_env(),
            dashboard=DashboardConfig.from_env(),
            alerting=AlertingConfig.from_env(),
            enabled=os.getenv("ICE_LOCATOR_MONITORING_ENABLED", "true").lower() == "true",
            privacy_mode=os.getenv("ICE_LOCATOR_PRIVACY_MODE", "strict"),
            data_retention_days=int(os.getenv("ICE_LOCATOR_DATA_RETENTION_DAYS", "30")),
            export_logs_to_file=os.getenv("ICE_LOCATOR_EXPORT_LOGS", "true").lower() == "true"
        )
    
    def validate(self) -> bool:
        """Validate monitoring configuration."""
        
        if not self.enabled:
            return True
        
        # Check privacy mode
        valid_privacy_modes = ["strict", "moderate", "disabled"]
        if self.privacy_mode not in valid_privacy_modes:
            raise ValueError(f"Invalid privacy mode: {self.privacy_mode}")
        
        # Check data retention
        if self.data_retention_days < 1:
            raise ValueError("Data retention must be at least 1 day")
        
        # Check log file path
        if self.export_logs_to_file and self.log_file_path:
            try:
                self.log_file_path.parent.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                raise ValueError(f"Cannot create log directory: {e}")
        
        return True
    
    def get_privacy_settings(self) -> Dict[str, Any]:
        """Get privacy-related settings for all monitoring components."""
        
        privacy_settings = {
            "redaction_level": "strict" if self.privacy_mode == "strict" else "moderate",
            "include_sensitive_data": self.privacy_mode == "disabled",
            "local_only_mode": self.privacy_mode == "strict",
            "data_retention_days": self.data_retention_days
        }
        
        return privacy_settings
    
    def get_exporter_configs(self) -> Dict[str, Any]:
        """Get configurations for all telemetry exporters."""
        
        configs = {}
        
        # MCPcat configuration
        if self.mcpcat.enabled:
            configs["mcpcat"] = {
                "enabled": True,
                "project_id": self.mcpcat.project_id,
                "redaction_level": self.mcpcat.redaction_level,
                "local_only": self.mcpcat.local_only
            }
        
        # Telemetry exporters
        if self.telemetry.enabled:
            configs.update(self.telemetry.exporters)
        
        return configs
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        
        return {
            "enabled": self.enabled,
            "privacy_mode": self.privacy_mode,
            "data_retention_days": self.data_retention_days,
            "mcpcat": {
                "enabled": self.mcpcat.enabled,
                "project_id": self.mcpcat.project_id[:8] + "..." if self.mcpcat.project_id else None,
                "redaction_level": self.mcpcat.redaction_level,
                "local_only": self.mcpcat.local_only
            },
            "telemetry": {
                "enabled": self.telemetry.enabled,
                "exporters": list(self.telemetry.exporters.keys()),
                "sampling_rate": self.telemetry.sampling_rate
            },
            "os_monitoring": {
                "enabled": self.os_monitoring.enabled,
                "collection_interval": self.os_monitoring.collection_interval,
                "metrics_count": len(self.os_monitoring.metrics_to_collect)
            },
            "dashboard": {
                "enabled": self.dashboard.enabled,
                "port": self.dashboard.port,
                "include_sensitive_data": self.dashboard.include_sensitive_data
            },
            "alerting": {
                "enabled": self.alerting.enabled,
                "channels_count": len(self.alerting.alert_channels),
                "thresholds": self.alerting.thresholds
            }
        }


def load_monitoring_config(config_file: Optional[Path] = None) -> MonitoringConfig:
    """Load monitoring configuration from file or environment."""
    
    if config_file and config_file.exists():
        # Load from YAML/JSON file if provided
        import json
        try:
            with open(config_file, 'r') as f:
                if config_file.suffix.lower() == '.json':
                    config_data = json.load(f)
                else:
                    # YAML support if available
                    try:
                        import yaml
                        config_data = yaml.safe_load(f)
                    except ImportError:
                        raise ValueError("YAML support not available - install PyYAML")
            
            # Convert to MonitoringConfig (simplified)
            return MonitoringConfig.from_env()  # For now, use env vars
            
        except Exception as e:
            raise ValueError(f"Failed to load config file: {e}")
    
    # Default: load from environment variables
    return MonitoringConfig.from_env()