"""
Advanced anti-detection module for ICE Locator MCP Server.

This module provides comprehensive anti-detection capabilities including:
- Proxy management with health monitoring and analytics
- Request obfuscation and browser fingerprinting
- Behavioral simulation for human-like patterns
- Traffic distribution and intelligent request spacing
- CAPTCHA detection and handling
- Adaptive timing based on success/failure rates
"""

from .proxy_manager import ProxyManager, ProxyConfig, ProxyMetrics, ProxyStatus
from .request_obfuscator import RequestObfuscator, BrowserProfile, RequestContext
from .behavioral_simulator import BehavioralSimulator, BehaviorType, SessionPhase, BrowsingSession
from .traffic_distributor import TrafficDistributor, TrafficPattern, RequestPriority, TrafficMetrics
from .coordinator import AntiDetectionCoordinator

__all__ = [
    "ProxyManager",
    "ProxyConfig", 
    "ProxyMetrics",
    "ProxyStatus",
    "RequestObfuscator",
    "BrowserProfile",
    "RequestContext",
    "BehavioralSimulator",
    "BehaviorType",
    "SessionPhase", 
    "BrowsingSession",
    "TrafficDistributor",
    "TrafficPattern",
    "RequestPriority",
    "TrafficMetrics",
    "AntiDetectionCoordinator"
]