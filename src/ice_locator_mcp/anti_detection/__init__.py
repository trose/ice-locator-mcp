"""
Anti-detection module for ICE Locator MCP Server.

This module provides comprehensive anti-detection capabilities including:
- Proxy management and IP rotation
- Request obfuscation and header randomization
- Behavioral simulation for human-like patterns
- CAPTCHA detection and handling
"""

from .proxy_manager import ProxyManager, ProxyConfig, ProxyMetrics, ProxyStatus
from .request_obfuscator import RequestObfuscator, BrowserProfile, RequestContext

__all__ = [
    "ProxyManager",
    "ProxyConfig", 
    "ProxyMetrics",
    "ProxyStatus",
    "RequestObfuscator",
    "BrowserProfile",
    "RequestContext"
]