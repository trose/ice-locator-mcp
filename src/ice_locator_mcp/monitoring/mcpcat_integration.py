"""
MCPcat analytics integration with privacy-first data collection.

Provides comprehensive analytics for MCP server usage using the
official MCPcat Python SDK with automatic data redaction.
"""

import os
import time
import asyncio
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
import structlog

try:
    import mcpcat
    from mcpcat import MCPCatOptions, UserIdentity
    try:
        from mcpcat import ExporterConfig
    except ImportError:
        ExporterConfig = None
    MCPCAT_AVAILABLE = True
except ImportError:
    MCPCAT_AVAILABLE = False
    mcpcat = None
    MCPCatOptions = None
    UserIdentity = None
    ExporterConfig = None

from .privacy_redaction import DataRedactor, RedactionConfig
from ..core.config import MonitoringConfig

# Defer import to avoid circular dependency
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..core.config import ServerConfig


logger = structlog.get_logger(__name__)

# Default project ID from mcpcat.io setup
DEFAULT_PROJECT_ID = "proj_31wD5K62DcuF4XH65PCrsyv7MIO"


@dataclass
class MCPcatConfig:
    """Configuration for MCPcat integration."""
    
    enabled: bool = True
    project_id: str = DEFAULT_PROJECT_ID
    redaction_level: str = "strict"
    identify_users: bool = False  # Disabled by default for privacy
    
    @classmethod
    def from_env(cls) -> "MCPcatConfig":
        """Create configuration from environment variables."""
        return cls(
            enabled=os.getenv("ICE_LOCATOR_ANALYTICS_ENABLED", "true").lower() == "true",
            project_id=os.getenv("ICE_LOCATOR_MCPCAT_PROJECT_ID", DEFAULT_PROJECT_ID),
            redaction_level=os.getenv("ICE_LOCATOR_REDACTION_LEVEL", "strict"),
            identify_users=os.getenv("ICE_LOCATOR_IDENTIFY_USERS", "false").lower() == "true"
        )


class MCPcatMonitor:
    """Privacy-first MCPcat analytics integration using official Python SDK."""
    
    def __init__(self, config: MCPcatConfig = None, 
                 telemetry_exporter = None):
        self.config = config or MCPcatConfig.from_env()
        self.telemetry_exporter = telemetry_exporter
        self.logger = structlog.get_logger(__name__)
        self.redactor = DataRedactor(RedactionConfig(
            redaction_level=self.config.redaction_level
        ))
        
        # Analytics state
        self.session_metrics: Dict[str, Dict[str, Any]] = {}
        self.tool_usage_stats: Dict[str, int] = {}
        self.performance_metrics: Dict[str, float] = {}
        self.is_initialized = False
        
        # Validation
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate MCPcat configuration."""
        
        if not self.config.enabled:
            self.logger.info("MCPcat analytics disabled")
            return
        
        if not MCPCAT_AVAILABLE:
            self.logger.warning(
                "MCPcat not available - install with: pip install mcpcat"
            )
            self.config.enabled = False
            return
        
        self.logger.info(
            "MCPcat configuration validated",
            project_id=self.config.project_id[:8] + "..." if self.config.project_id else "None",
            redaction_level=self.config.redaction_level
        )
    
    def setup_tracking(self, server) -> None:
        """Set up MCPcat tracking with the MCP server.
        
        This should be called during server initialization, after all tools are registered.
        """
        
        if not self.config.enabled or not MCPCAT_AVAILABLE:
            self.logger.info("MCPcat tracking not enabled")
            return
        
        try:
            # Configure MCPcat options
            options = MCPCatOptions()
            
            # Set up user identification if enabled (disabled by default for privacy)
            if self.config.identify_users:
                options.identify = self._create_user_identifier()
            
            # Set up data redaction
            options.redact_sensitive_information = self._redact_analytics_data
            
            # Set up telemetry exporters if available
            if self.telemetry_exporter and hasattr(self.telemetry_exporter, 'config'):
                options.exporters = self._setup_telemetry_exporters()
            
            # Initialize tracking with the server and project ID
            mcpcat.track(server, self.config.project_id, options)
            
            self.is_initialized = True
            
            self.logger.info(
                "MCPcat tracking initialized successfully",
                project_id=self.config.project_id[:8] + "...",
                redaction_level=self.config.redaction_level,
                user_identification=self.config.identify_users
            )
                
        except Exception as e:
            self.logger.error(
                "Failed to initialize MCPcat tracking",
                error=str(e),
                project_id=self.config.project_id[:8] + "..." if self.config.project_id else "None"
            )
            self.config.enabled = False
    
    def _setup_telemetry_exporters(self) -> Dict[str, Any]:
        """Set up telemetry exporters for MCPcat."""
        exporters = {}
        
        if not self.telemetry_exporter or ExporterConfig is None:
            return exporters
        
        try:
            # Get telemetry config from the exporter
            tel_config = self.telemetry_exporter.config
            
            # Add configured exporters
            for name, exporter_config in tel_config.exporters.items():
                if name == "datadog" and exporter_config.get("enabled"):
                    exporters["datadog"] = ExporterConfig(
                        type="datadog",
                        api_key=exporter_config.get("api_key"),
                        site=exporter_config.get("site", "datadoghq.com"),
                        service="ice-locator-mcp"
                    )
                
                elif name == "sentry" and exporter_config.get("enabled"):
                    exporters["sentry"] = ExporterConfig(
                        type="sentry",
                        dsn=exporter_config.get("dsn"),
                        environment=exporter_config.get("environment", "production")
                    )
                
                elif name == "otlp" and exporter_config.get("enabled"):
                    exporters["otlp"] = ExporterConfig(
                        type="otlp",
                        endpoint=exporter_config.get("endpoint", "http://localhost:4318/v1/traces")
                    )
            
            self.logger.info("Telemetry exporters configured", exporters=list(exporters.keys()))
            
        except Exception as e:
            self.logger.error("Failed to setup telemetry exporters", error=str(e))
        
        return exporters
    
    def _create_user_identifier(self) -> Callable:
        """Create user identification function (privacy-conscious)."""
        
        def identify_user(request, extra) -> UserIdentity:
            """Identify user session without collecting personal data."""
            
            # Generate anonymous session ID based on request patterns
            session_data = {
                "client_type": self._detect_client_type(request),
                "session_hash": self._generate_session_hash(request),
                "language_preference": self._detect_language_preference(request)
            }
            
            return UserIdentity(
                user_id=session_data["session_hash"],
                user_data=session_data
            )
        
        return identify_user
    
    def _redact_analytics_data(self, text: str) -> str:
        """Redact sensitive information from analytics data."""
        
        if not isinstance(text, str):
            return text
        
        # Apply comprehensive redaction
        return self.redactor._redact_patterns(text)
    
    def track_tool_usage(self, tool_name: str, parameters: Dict[str, Any], 
                        result: Dict[str, Any], execution_time: float) -> None:
        """Track tool usage with privacy protection."""
        
        if not self.config.enabled:
            return
        
        try:
            # Redact sensitive information
            redacted_params = self.redactor.redact_search_query(parameters)
            redacted_result = self.redactor.redact_search_results(result)
            
            # Update local statistics
            self.tool_usage_stats[tool_name] = self.tool_usage_stats.get(tool_name, 0) + 1
            
            # Track performance metrics
            performance_key = f"{tool_name}_performance"
            if performance_key not in self.performance_metrics:
                self.performance_metrics[performance_key] = execution_time
            else:
                # Exponential moving average
                self.performance_metrics[performance_key] = (
                    self.performance_metrics[performance_key] * 0.8 + 
                    execution_time * 0.2
                )
            
            # Log analytics event (redacted)
            self.logger.info(
                "Tool usage tracked",
                tool=tool_name,
                execution_time=execution_time,
                success=result.get("status") == "found",
                parameters_redacted=True,
                results_redacted=True
            )
            
        except Exception as e:
            self.logger.error(
                "Failed to track tool usage",
                tool=tool_name,
                error=str(e)
            )
    
    def track_search_pattern(self, search_type: str, success: bool, 
                           processing_time: float, result_count: int = 0) -> None:
        """Track search patterns for analytics."""
        
        if not self.config.enabled:
            return
        
        try:
            # Create anonymized search pattern data
            pattern_data = {
                "search_type": search_type,
                "success": success,
                "processing_time": processing_time,
                "result_count": result_count if success else 0,
                "timestamp": time.time()
            }
            
            # Update session metrics
            session_id = "current_session"  # Simplified for now
            if session_id not in self.session_metrics:
                self.session_metrics[session_id] = {
                    "search_count": 0,
                    "success_count": 0,
                    "total_time": 0.0,
                    "search_types": {}
                }
            
            session = self.session_metrics[session_id]
            session["search_count"] += 1
            session["total_time"] += processing_time
            
            if success:
                session["success_count"] += 1
            
            session["search_types"][search_type] = session["search_types"].get(search_type, 0) + 1
            
            self.logger.debug(
                "Search pattern tracked",
                search_type=search_type,
                success=success,
                processing_time=processing_time
            )
            
        except Exception as e:
            self.logger.error(
                "Failed to track search pattern",
                error=str(e)
            )
    
    def track_error(self, error_type: str, error_context: Dict[str, Any]) -> None:
        """Track errors for debugging and improvement."""
        
        if not self.config.enabled:
            return
        
        try:
            # Redact sensitive information from error context
            redacted_context = self.redactor.redact_analytics_data(error_context)
            
            self.logger.info(
                "Error tracked for analytics",
                error_type=error_type,
                context_redacted=True
            )
            
        except Exception as e:
            self.logger.error(
                "Failed to track error",
                error=str(e)
            )
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get summary of analytics data (redacted)."""
        
        try:
            total_searches = sum(self.tool_usage_stats.values())
            
            summary = {
                "analytics_enabled": self.config.enabled,
                "redaction_level": self.config.redaction_level,
                "total_tool_usage": total_searches,
                "tool_distribution": self.tool_usage_stats.copy(),
                "performance_metrics": self.performance_metrics.copy(),
                "session_count": len(self.session_metrics),
                "privacy_protection": {
                    "data_redaction": True,
                    "local_processing": True,
                    "no_personal_data": True,
                    "open_source_redaction": True
                }
            }
            
            # Calculate aggregated metrics
            if self.session_metrics:
                total_success = sum(
                    session["success_count"] 
                    for session in self.session_metrics.values()
                )
                total_attempts = sum(
                    session["search_count"] 
                    for session in self.session_metrics.values()
                )
                
                summary["success_rate"] = total_success / total_attempts if total_attempts > 0 else 0
                summary["average_processing_time"] = sum(self.performance_metrics.values()) / len(self.performance_metrics) if self.performance_metrics else 0
            
            return summary
            
        except Exception as e:
            self.logger.error("Failed to generate analytics summary", error=str(e))
            return {"error": "Failed to generate summary"}
    
    def _detect_client_type(self, request) -> str:
        """Detect the type of MCP client being used."""
        
        # Analyze request patterns to identify client type
        # This is anonymous and doesn't collect personal data
        
        if hasattr(request, 'headers'):
            user_agent = request.headers.get('User-Agent', '').lower()
            if 'claude' in user_agent:
                return 'claude_desktop'
            elif 'cursor' in user_agent:
                return 'cursor_ide'
            elif 'continue' in user_agent:
                return 'continue'
        
        return 'unknown'
    
    def _generate_session_hash(self, request) -> str:
        """Generate anonymous session identifier."""
        
        import hashlib
        
        # Create hash based on non-personal request characteristics
        session_data = f"{time.time()//3600}_{self._detect_client_type(request)}"
        return hashlib.md5(session_data.encode()).hexdigest()[:12]
    
    def _detect_language_preference(self, request) -> str:
        """Detect language preference from request patterns."""
        
        # Simple detection based on request patterns (not content)
        if hasattr(request, 'params') and hasattr(request.params, 'arguments'):
            args = request.params.arguments
            if isinstance(args, dict):
                if args.get('language') == 'es':
                    return 'spanish'
                elif 'Spanish' in str(args.get('query', '')):
                    return 'spanish'
        
        return 'english'
    
    async def cleanup(self) -> None:
        """Cleanup analytics resources."""
        
        if self.config.enabled:
            self.logger.info(
                "MCPcat analytics cleanup",
                total_sessions=len(self.session_metrics),
                tool_usage_count=sum(self.tool_usage_stats.values())
            )
        
        # Clear local data
        self.session_metrics.clear()
        self.tool_usage_stats.clear()
        self.performance_metrics.clear()


def create_monitor(config: "ServerConfig" = None) -> MCPcatMonitor:
    """Create MCPcat monitor with server configuration."""
    
    if config and hasattr(config, 'monitoring_config'):
        mcpcat_config = MCPcatConfig(
            enabled=config.monitoring_config.mcpcat_enabled,
            project_id=config.monitoring_config.mcpcat_project_id,
            redaction_level=config.monitoring_config.redaction_level
        )
    else:
        mcpcat_config = MCPcatConfig.from_env()
    
    return MCPcatMonitor(mcpcat_config)