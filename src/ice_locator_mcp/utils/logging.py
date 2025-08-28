"""
Logging utilities for ICE Locator MCP Server.
"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional
import structlog
from structlog.stdlib import LoggerFactory


def setup_logging(
    level: str = "INFO",
    log_format: str = "json",
    log_file: Optional[Path] = None,
    console_output: bool = True
) -> None:
    """Setup structured logging for the application."""
    
    # Configure structlog processors
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    
    # Add appropriate formatter based on format choice
    if log_format.lower() == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=console_output))
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout if console_output else None,
        level=getattr(logging, level.upper())
    )
    
    # Add file handler if specified
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, level.upper()))
        
        if log_format.lower() == "json":
            file_formatter = logging.Formatter('%(message)s')
        else:
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        file_handler.setFormatter(file_formatter)
        logging.getLogger().addHandler(file_handler)


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


class RequestLogger:
    """Logger for tracking request-response cycles."""
    
    def __init__(self, logger_name: str = "request_logger"):
        self.logger = structlog.get_logger(logger_name)
    
    async def log_request(self,
                         request_id: str,
                         method: str,
                         url: str,
                         headers: Optional[Dict[str, str]] = None,
                         **kwargs) -> None:
        """Log an outgoing request."""
        self.logger.info(
            "Request sent",
            request_id=request_id,
            method=method,
            url=self._sanitize_url(url),
            headers=self._sanitize_headers(headers or {}),
            **kwargs
        )
    
    async def log_response(self,
                          request_id: str,
                          status_code: int,
                          response_time: float,
                          response_size: Optional[int] = None,
                          **kwargs) -> None:
        """Log a received response."""
        self.logger.info(
            "Response received",
            request_id=request_id,
            status_code=status_code,
            response_time_ms=int(response_time * 1000),
            response_size=response_size,
            **kwargs
        )
    
    async def log_error(self,
                       request_id: str,
                       error: Exception,
                       **kwargs) -> None:
        """Log a request error."""
        self.logger.error(
            "Request failed",
            request_id=request_id,
            error_type=type(error).__name__,
            error_message=str(error),
            **kwargs
        )
    
    def _sanitize_url(self, url: str) -> str:
        """Remove sensitive information from URL."""
        # Remove query parameters that might contain sensitive data
        if '?' in url:
            base_url = url.split('?')[0]
            return f"{base_url}?[parameters_hidden]"
        return url
    
    def _sanitize_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Remove sensitive information from headers."""
        sensitive_headers = {
            'authorization', 'cookie', 'x-api-key', 'x-auth-token'
        }
        
        sanitized = {}
        for key, value in headers.items():
            if key.lower() in sensitive_headers:
                sanitized[key] = "[REDACTED]"
            else:
                sanitized[key] = value
        
        return sanitized


class PerformanceLogger:
    """Logger for tracking performance metrics."""
    
    def __init__(self, logger_name: str = "performance_logger"):
        self.logger = structlog.get_logger(logger_name)
    
    async def log_search_performance(self,
                                   search_type: str,
                                   processing_time: float,
                                   cache_hit: bool,
                                   results_count: int,
                                   **kwargs) -> None:
        """Log search performance metrics."""
        self.logger.info(
            "Search performance",
            search_type=search_type,
            processing_time_ms=int(processing_time * 1000),
            cache_hit=cache_hit,
            results_count=results_count,
            **kwargs
        )
    
    async def log_proxy_performance(self,
                                  proxy_endpoint: str,
                                  response_time: float,
                                  success: bool,
                                  **kwargs) -> None:
        """Log proxy performance metrics."""
        self.logger.info(
            "Proxy performance",
            proxy_endpoint=self._sanitize_proxy_endpoint(proxy_endpoint),
            response_time_ms=int(response_time * 1000),
            success=success,
            **kwargs
        )
    
    async def log_rate_limit_metrics(self,
                                   requests_per_minute: float,
                                   burst_usage: int,
                                   wait_time: float,
                                   **kwargs) -> None:
        """Log rate limiting metrics."""
        self.logger.info(
            "Rate limit metrics",
            requests_per_minute=requests_per_minute,
            burst_usage=burst_usage,
            wait_time_ms=int(wait_time * 1000),
            **kwargs
        )
    
    def _sanitize_proxy_endpoint(self, endpoint: str) -> str:
        """Sanitize proxy endpoint for logging."""
        # Keep just the host part, remove credentials
        if '@' in endpoint:
            endpoint = endpoint.split('@')[-1]
        return endpoint


class SecurityLogger:
    """Logger for security-related events."""
    
    def __init__(self, logger_name: str = "security_logger"):
        self.logger = structlog.get_logger(logger_name)
    
    async def log_captcha_detected(self,
                                 request_id: str,
                                 captcha_type: str,
                                 **kwargs) -> None:
        """Log CAPTCHA detection."""
        self.logger.warning(
            "CAPTCHA detected",
            request_id=request_id,
            captcha_type=captcha_type,
            **kwargs
        )
    
    async def log_rate_limit_hit(self,
                               request_id: str,
                               limit_type: str,
                               **kwargs) -> None:
        """Log rate limit hit."""
        self.logger.warning(
            "Rate limit hit",
            request_id=request_id,
            limit_type=limit_type,
            **kwargs
        )
    
    async def log_proxy_failure(self,
                              proxy_endpoint: str,
                              failure_reason: str,
                              **kwargs) -> None:
        """Log proxy failure."""
        self.logger.warning(
            "Proxy failure",
            proxy_endpoint=self._sanitize_proxy_endpoint(proxy_endpoint),
            failure_reason=failure_reason,
            **kwargs
        )
    
    async def log_suspicious_activity(self,
                                    activity_type: str,
                                    details: Dict[str, Any],
                                    **kwargs) -> None:
        """Log suspicious activity."""
        self.logger.error(
            "Suspicious activity detected",
            activity_type=activity_type,
            details=details,
            **kwargs
        )
    
    def _sanitize_proxy_endpoint(self, endpoint: str) -> str:
        """Sanitize proxy endpoint for logging."""
        if '@' in endpoint:
            endpoint = endpoint.split('@')[-1]
        return endpoint