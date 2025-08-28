"""
Advanced telemetry framework with multiple exporter support.

Integrates with OpenTelemetry, Datadog, and Sentry through MCPcat
for comprehensive observability and monitoring.
"""

import os
import time
import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import structlog

# Optional imports with graceful fallbacks
try:
    from opentelemetry import trace, metrics
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False
    trace = None
    metrics = None

try:
    import sentry_sdk
    from sentry_sdk.integrations.asyncio import AsyncioIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False
    sentry_sdk = None

try:
    from mcpcat import ExporterConfig
    MCPCAT_AVAILABLE = True
except ImportError:
    MCPCAT_AVAILABLE = False
    ExporterConfig = None

from .privacy_redaction import DataRedactor


logger = structlog.get_logger(__name__)


class ExporterType(Enum):
    """Types of telemetry exporters."""
    OTLP = "otlp"
    DATADOG = "datadog"
    SENTRY = "sentry"
    PROMETHEUS = "prometheus"
    JAEGER = "jaeger"


@dataclass
class TelemetryConfig:
    """Configuration for telemetry exporters."""
    
    enabled: bool = True
    exporters: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    sampling_rate: float = 0.1  # 10% sampling by default
    include_sensitive_spans: bool = False  # Privacy protection
    
    @classmethod
    def from_env(cls) -> "TelemetryConfig":
        """Create configuration from environment variables."""
        
        config = cls(
            enabled=os.getenv("ICE_LOCATOR_TELEMETRY_ENABLED", "true").lower() == "true",
            sampling_rate=float(os.getenv("ICE_LOCATOR_TELEMETRY_SAMPLING_RATE", "0.1"))
        )
        
        # Configure exporters from environment
        exporters = {}
        
        # OpenTelemetry/OTLP
        if os.getenv("OTLP_ENDPOINT"):
            exporters["otlp"] = {
                "type": "otlp",
                "endpoint": os.getenv("OTLP_ENDPOINT"),
                "headers": os.getenv("OTLP_HEADERS", "")
            }
        
        # Datadog
        if os.getenv("DD_API_KEY"):
            exporters["datadog"] = {
                "type": "datadog",
                "api_key": os.getenv("DD_API_KEY"),
                "site": os.getenv("DD_SITE", "datadoghq.com"),
                "service": os.getenv("DD_SERVICE", "ice-locator-mcp"),
                "env": os.getenv("DD_ENV", "production")
            }
        
        # Sentry
        if os.getenv("SENTRY_DSN"):
            exporters["sentry"] = {
                "type": "sentry",
                "dsn": os.getenv("SENTRY_DSN"),
                "environment": os.getenv("SENTRY_ENVIRONMENT", "production"),
                "traces_sample_rate": float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1"))
            }
        
        config.exporters = exporters
        return config


class TelemetryExporter:
    """Advanced telemetry framework with multiple exporter support."""
    
    def __init__(self, config: TelemetryConfig = None):
        self.config = config or TelemetryConfig.from_env()
        self.logger = structlog.get_logger(__name__)
        self.redactor = DataRedactor()
        
        # Telemetry providers
        self.tracer_provider: Optional[TracerProvider] = None
        self.meter_provider: Optional[MeterProvider] = None
        self.tracer = None
        self.meter = None
        
        # Performance tracking
        self.span_cache: Dict[str, Any] = {}
        self.metrics_cache: Dict[str, float] = {}
        
        # Initialize if enabled
        if self.config.enabled:
            self._initialize_telemetry()
    
    def _initialize_telemetry(self) -> None:
        """Initialize telemetry providers and exporters."""
        
        if not self.config.enabled:
            return
        
        try:
            # Initialize OpenTelemetry if available
            if OPENTELEMETRY_AVAILABLE:
                self._setup_opentelemetry()
            
            # Initialize Sentry if configured
            if "sentry" in self.config.exporters and SENTRY_AVAILABLE:
                self._setup_sentry()
            
            self.logger.info(
                "Telemetry framework initialized",
                exporters=list(self.config.exporters.keys()),
                sampling_rate=self.config.sampling_rate
            )
            
        except Exception as e:
            self.logger.error(
                "Failed to initialize telemetry framework",
                error=str(e)
            )
            self.config.enabled = False
    
    def _setup_opentelemetry(self) -> None:
        """Set up OpenTelemetry tracing and metrics."""
        
        if not OPENTELEMETRY_AVAILABLE:
            self.logger.warning("OpenTelemetry not available")
            return
        
        try:
            # Configure tracer provider
            self.tracer_provider = TracerProvider()
            trace.set_tracer_provider(self.tracer_provider)
            
            # Configure exporters
            for name, exporter_config in self.config.exporters.items():
                if exporter_config["type"] == "otlp":
                    self._setup_otlp_exporter(exporter_config)
                elif exporter_config["type"] == "jaeger":
                    self._setup_jaeger_exporter(exporter_config)
            
            # Get tracer and meter
            self.tracer = trace.get_tracer("ice-locator-mcp")
            
            # Configure metrics if available
            try:
                self.meter_provider = MeterProvider()
                metrics.set_meter_provider(self.meter_provider)
                self.meter = metrics.get_meter("ice-locator-mcp")
            except Exception as e:
                self.logger.warning("Metrics not available", error=str(e))
            
        except Exception as e:
            self.logger.error("Failed to setup OpenTelemetry", error=str(e))
    
    def _setup_otlp_exporter(self, config: Dict[str, Any]) -> None:
        """Set up OTLP exporter for OpenTelemetry."""
        
        try:
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
            
            exporter = OTLPSpanExporter(
                endpoint=config["endpoint"],
                headers=self._parse_headers(config.get("headers", ""))
            )
            
            processor = BatchSpanProcessor(exporter)
            self.tracer_provider.add_span_processor(processor)
            
            self.logger.info(
                "OTLP exporter configured",
                endpoint=config["endpoint"][:50] + "..." if len(config["endpoint"]) > 50 else config["endpoint"]
            )
            
        except ImportError:
            self.logger.warning("OTLP exporter not available - install with: pip install opentelemetry-exporter-otlp")
        except Exception as e:
            self.logger.error("Failed to setup OTLP exporter", error=str(e))
    
    def _setup_jaeger_exporter(self, config: Dict[str, Any]) -> None:
        """Set up Jaeger exporter for OpenTelemetry."""
        
        try:
            from opentelemetry.exporter.jaeger.thrift import JaegerExporter
            
            exporter = JaegerExporter(
                agent_host_name=config.get("agent_host", "localhost"),
                agent_port=config.get("agent_port", 6831),
            )
            
            processor = BatchSpanProcessor(exporter)
            self.tracer_provider.add_span_processor(processor)
            
            self.logger.info("Jaeger exporter configured")
            
        except ImportError:
            self.logger.warning("Jaeger exporter not available")
        except Exception as e:
            self.logger.error("Failed to setup Jaeger exporter", error=str(e))
    
    def _setup_sentry(self) -> None:
        """Set up Sentry error tracking and performance monitoring."""
        
        if not SENTRY_AVAILABLE:
            self.logger.warning("Sentry not available")
            return
        
        sentry_config = self.config.exporters.get("sentry", {})
        
        try:
            sentry_sdk.init(
                dsn=sentry_config["dsn"],
                environment=sentry_config.get("environment", "production"),
                traces_sample_rate=sentry_config.get("traces_sample_rate", 0.1),
                integrations=[
                    AsyncioIntegration(),
                    LoggingIntegration(level=None, event_level=None)
                ],
                before_send=self._redact_sentry_data,
                before_send_transaction=self._redact_sentry_transaction
            )
            
            self.logger.info("Sentry integration configured")
            
        except Exception as e:
            self.logger.error("Failed to setup Sentry", error=str(e))
    
    def _redact_sentry_data(self, event, hint):
        """Redact sensitive data from Sentry events."""
        
        try:
            # Redact sensitive information from event data
            if 'message' in event:
                event['message'] = self.redactor._redact_patterns(event['message'])
            
            if 'extra' in event:
                event['extra'] = self.redactor.redact_analytics_data(event['extra'])
            
            if 'contexts' in event:
                event['contexts'] = self.redactor.redact_analytics_data(event['contexts'])
            
            return event
            
        except Exception as e:
            self.logger.error("Failed to redact Sentry data", error=str(e))
            return event
    
    def _redact_sentry_transaction(self, event, hint):
        """Redact sensitive data from Sentry transactions."""
        
        try:
            # Redact transaction names and tags
            if 'transaction' in event:
                event['transaction'] = self.redactor._redact_patterns(event['transaction'])
            
            if 'tags' in event:
                event['tags'] = self.redactor.redact_analytics_data(event['tags'])
            
            return event
            
        except Exception as e:
            self.logger.error("Failed to redact Sentry transaction", error=str(e))
            return event
    
    def start_span(self, name: str, attributes: Dict[str, Any] = None) -> str:
        """Start a new telemetry span with privacy protection."""
        
        if not self.config.enabled or not self.tracer:
            return f"span_{int(time.time() * 1000)}"
        
        try:
            # Redact sensitive attributes
            safe_attributes = {}
            if attributes:
                safe_attributes = self.redactor.redact_analytics_data(attributes)
            
            # Create span
            span = self.tracer.start_span(
                name=self.redactor._redact_patterns(name),
                attributes=safe_attributes
            )
            
            span_id = f"span_{id(span)}"
            self.span_cache[span_id] = span
            
            return span_id
            
        except Exception as e:
            self.logger.error("Failed to start span", error=str(e))
            return f"span_error_{int(time.time() * 1000)}"
    
    def end_span(self, span_id: str, status: str = "ok", attributes: Dict[str, Any] = None) -> None:
        """End a telemetry span."""
        
        if not self.config.enabled:
            return
        
        try:
            span = self.span_cache.pop(span_id, None)
            if not span:
                return
            
            # Add final attributes
            if attributes:
                safe_attributes = self.redactor.redact_analytics_data(attributes)
                for key, value in safe_attributes.items():
                    span.set_attribute(key, value)
            
            # Set status
            if status == "error":
                span.set_status(trace.Status(trace.StatusCode.ERROR))
            else:
                span.set_status(trace.Status(trace.StatusCode.OK))
            
            span.end()
            
        except Exception as e:
            self.logger.error("Failed to end span", span_id=span_id, error=str(e))
    
    def record_metric(self, name: str, value: float, attributes: Dict[str, Any] = None) -> None:
        """Record a metric value."""
        
        if not self.config.enabled or not self.meter:
            return
        
        try:
            # Redact attributes
            safe_attributes = {}
            if attributes:
                safe_attributes = self.redactor.redact_analytics_data(attributes)
            
            # Record metric (simplified - would use proper meter instruments)
            self.metrics_cache[name] = value
            
            self.logger.debug(
                "Metric recorded",
                name=name,
                value=value
            )
            
        except Exception as e:
            self.logger.error("Failed to record metric", error=str(e))
    
    def record_search_operation(self, operation_type: str, success: bool, 
                              duration: float, result_count: int = 0) -> None:
        """Record search operation metrics."""
        
        if not self.config.enabled:
            return
        
        try:
            # Start span for search operation
            span_id = self.start_span(
                f"search_{operation_type}",
                {
                    "operation.type": operation_type,
                    "operation.duration": duration,
                    "operation.success": success,
                    "result.count": result_count if success else 0
                }
            )
            
            # Record metrics
            self.record_metric(f"search_{operation_type}_duration", duration)
            self.record_metric(f"search_{operation_type}_success", 1.0 if success else 0.0)
            
            # End span
            self.end_span(
                span_id, 
                "ok" if success else "error",
                {"final.result_count": result_count}
            )
            
        except Exception as e:
            self.logger.error("Failed to record search operation", error=str(e))
    
    def record_error(self, error: Exception, context: Dict[str, Any] = None) -> None:
        """Record error information."""
        
        if not self.config.enabled:
            return
        
        try:
            # Redact context
            safe_context = {}
            if context:
                safe_context = self.redactor.redact_analytics_data(context)
            
            # Record to Sentry if available
            if SENTRY_AVAILABLE and "sentry" in self.config.exporters:
                with sentry_sdk.push_scope() as scope:
                    for key, value in safe_context.items():
                        scope.set_extra(key, value)
                    sentry_sdk.capture_exception(error)
            
            # Record span
            span_id = self.start_span(
                "error_occurred",
                {
                    "error.type": type(error).__name__,
                    "error.message": self.redactor._redact_patterns(str(error)),
                    **safe_context
                }
            )
            self.end_span(span_id, "error")
            
        except Exception as e:
            self.logger.error("Failed to record error", error=str(e))
    
    def get_mcpcat_exporters(self) -> Dict[str, Any]:
        """Get exporter configurations for MCPcat integration."""
        
        if not MCPCAT_AVAILABLE:
            return {}
        
        exporters = {}
        
        for name, config in self.config.exporters.items():
            try:
                if config["type"] == "otlp":
                    exporters[name] = ExporterConfig(
                        type="otlp",
                        endpoint=config["endpoint"]
                    )
                elif config["type"] == "datadog":
                    exporters[name] = ExporterConfig(
                        type="datadog",
                        api_key=config["api_key"],
                        site=config.get("site", "datadoghq.com"),
                        service=config.get("service", "ice-locator-mcp")
                    )
                elif config["type"] == "sentry":
                    exporters[name] = ExporterConfig(
                        type="sentry",
                        dsn=config["dsn"],
                        environment=config.get("environment", "production")
                    )
            except Exception as e:
                self.logger.error(
                    "Failed to configure exporter for MCPcat",
                    exporter=name,
                    error=str(e)
                )
        
        return exporters
    
    def _parse_headers(self, headers_str: str) -> Dict[str, str]:
        """Parse headers string into dictionary."""
        
        headers = {}
        if not headers_str:
            return headers
        
        try:
            for header in headers_str.split(","):
                if "=" in header:
                    key, value = header.split("=", 1)
                    headers[key.strip()] = value.strip()
        except Exception as e:
            self.logger.error("Failed to parse headers", error=str(e))
        
        return headers
    
    async def cleanup(self) -> None:
        """Cleanup telemetry resources."""
        
        if self.config.enabled:
            # End any remaining spans
            for span_id, span in self.span_cache.items():
                try:
                    span.end()
                except Exception:
                    pass
            
            self.span_cache.clear()
            self.metrics_cache.clear()
            
            self.logger.info("Telemetry framework cleanup completed")


def create_telemetry_exporter(config: TelemetryConfig = None) -> TelemetryExporter:
    """Create telemetry exporter with configuration."""
    return TelemetryExporter(config)