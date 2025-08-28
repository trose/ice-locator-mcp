"""
Configuration management for ICE Locator MCP Server.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from pathlib import Path


@dataclass 
class ProxyConfig:
    """Configuration for proxy management."""
    
    enabled: bool = True
    rotation_interval: int = 300  # 5 minutes
    max_requests_per_proxy: int = 10
    health_check_interval: int = 60  # 1 minute
    retry_failed_after: int = 1800  # 30 minutes
    proxy_sources: List[str] = field(default_factory=lambda: [
        "free-proxy-list",
        "proxy-daily", 
        "ssl-proxies"
    ])
    residential_preferred: bool = True
    geographic_distribution: bool = True
    
    @property
    def proxy_list_file(self) -> Optional[Path]:
        """Path to custom proxy list file."""
        proxy_file = os.getenv("ICE_LOCATOR_PROXY_FILE")
        return Path(proxy_file) if proxy_file else None


@dataclass
class SearchConfig:
    """Configuration for search operations."""
    
    base_url: str = "https://locator.ice.gov"
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 2.0
    user_agent_rotation: bool = True
    session_duration: int = 1800  # 30 minutes
    
    # Rate limiting
    requests_per_minute: int = 10
    burst_allowance: int = 20
    
    # Fuzzy matching
    fuzzy_threshold: float = 0.7
    name_similarity_threshold: float = 0.8
    date_tolerance_days: int = 3
    
    # Behavioral simulation
    human_delays: bool = True
    min_delay: float = 1.0
    max_delay: float = 5.0
    typing_simulation: bool = True
    page_reading_simulation: bool = True


@dataclass
class CacheConfig:
    """Configuration for caching."""
    
    enabled: bool = True
    backend: str = "diskcache"  # diskcache, memory
    ttl: int = 3600  # 1 hour
    max_size: int = 1000  # Max number of cached items
    cache_dir: Path = field(default_factory=lambda: Path.home() / ".cache" / "ice-locator-mcp")
    
    # Cache policies
    cache_successful_searches: bool = True
    cache_failed_searches: bool = False
    cache_not_found_results: bool = True
    not_found_ttl: int = 300  # 5 minutes


@dataclass
class SecurityConfig:
    """Configuration for security and privacy."""
    
    log_sensitive_data: bool = False
    encrypt_cache: bool = False
    data_retention_days: int = 30
    anonymize_logs: bool = True
    
    # Rate limiting
    global_rate_limit: bool = True
    per_ip_rate_limit: bool = True
    
    # Anti-detection
    randomize_fingerprints: bool = True
    behavioral_simulation: bool = True
    traffic_obfuscation: bool = True


@dataclass
class LoggingConfig:
    """Configuration for logging."""
    
    level: str = "INFO"
    format: str = "json"  # json, text
    file_enabled: bool = True
    console_enabled: bool = True
    log_dir: Path = field(default_factory=lambda: Path.home() / ".logs" / "ice-locator-mcp")
    max_file_size: int = 10_000_000  # 10MB
    backup_count: int = 5
    
    # Structured logging
    include_timestamps: bool = True
    include_request_ids: bool = True
    include_performance_metrics: bool = True


@dataclass
class MonitoringConfig:
    """Configuration for monitoring and analytics."""
    
    mcpcat_enabled: bool = True
    mcpcat_project_id: Optional[str] = None
    redaction_level: str = "strict"  # strict, moderate, minimal
    identify_users: bool = False  # Disabled by default for privacy
    local_only: bool = False  # If True, no data sent to external servers
    
    @classmethod
    def from_env(cls) -> "MonitoringConfig":
        """Create monitoring configuration from environment variables."""
        return cls(
            mcpcat_enabled=os.getenv("ICE_LOCATOR_ANALYTICS_ENABLED", "true").lower() == "true",
            mcpcat_project_id=os.getenv("ICE_LOCATOR_MCPCAT_PROJECT_ID"),
            redaction_level=os.getenv("ICE_LOCATOR_REDACTION_LEVEL", "strict"),
            identify_users=os.getenv("ICE_LOCATOR_IDENTIFY_USERS", "false").lower() == "true",
            local_only=os.getenv("ICE_LOCATOR_ANALYTICS_LOCAL_ONLY", "false").lower() == "true"
        )


@dataclass
class ServerConfig:
    """Main server configuration."""
    
    # Sub-configurations
    proxy_config: ProxyConfig = field(default_factory=ProxyConfig)
    search_config: SearchConfig = field(default_factory=SearchConfig)
    cache_config: CacheConfig = field(default_factory=CacheConfig) 
    security_config: SecurityConfig = field(default_factory=SecurityConfig)
    logging_config: LoggingConfig = field(default_factory=LoggingConfig)
    monitoring_config: MonitoringConfig = field(default_factory=MonitoringConfig)
    
    # Server settings
    server_name: str = "ice-locator-mcp"
    server_version: str = "0.1.0"
    max_concurrent_requests: int = 10
    request_timeout: int = 60
    
    # Feature flags
    enhanced_search_enabled: bool = True
    bulk_search_enabled: bool = True
    reporting_enabled: bool = True
    monitoring_enabled: bool = True
    
    @classmethod
    def from_env(cls) -> "ServerConfig":
        """Create configuration from environment variables."""
        
        config = cls()
        
        # Proxy configuration
        if os.getenv("ICE_LOCATOR_PROXY_ENABLED"):
            config.proxy_config.enabled = os.getenv("ICE_LOCATOR_PROXY_ENABLED").lower() == "true"
        
        if os.getenv("ICE_LOCATOR_PROXY_ROTATION_INTERVAL"):
            config.proxy_config.rotation_interval = int(os.getenv("ICE_LOCATOR_PROXY_ROTATION_INTERVAL"))
            
        # Search configuration
        if os.getenv("ICE_LOCATOR_REQUESTS_PER_MINUTE"):
            config.search_config.requests_per_minute = int(os.getenv("ICE_LOCATOR_REQUESTS_PER_MINUTE"))
            
        if os.getenv("ICE_LOCATOR_TIMEOUT"):
            config.search_config.timeout = int(os.getenv("ICE_LOCATOR_TIMEOUT"))
        
        # Cache configuration
        if os.getenv("ICE_LOCATOR_CACHE_ENABLED"):
            config.cache_config.enabled = os.getenv("ICE_LOCATOR_CACHE_ENABLED").lower() == "true"
            
        if os.getenv("ICE_LOCATOR_CACHE_TTL"):
            config.cache_config.ttl = int(os.getenv("ICE_LOCATOR_CACHE_TTL"))
            
        if os.getenv("ICE_LOCATOR_CACHE_DIR"):
            config.cache_config.cache_dir = Path(os.getenv("ICE_LOCATOR_CACHE_DIR"))
        
        # Logging configuration
        if os.getenv("ICE_LOCATOR_LOG_LEVEL"):
            config.logging_config.level = os.getenv("ICE_LOCATOR_LOG_LEVEL")
            
        if os.getenv("ICE_LOCATOR_LOG_DIR"):
            config.logging_config.log_dir = Path(os.getenv("ICE_LOCATOR_LOG_DIR"))
        
        # Security configuration
        if os.getenv("ICE_LOCATOR_LOG_SENSITIVE_DATA"):
            config.security_config.log_sensitive_data = os.getenv("ICE_LOCATOR_LOG_SENSITIVE_DATA").lower() == "true"
        
        return config
    
    def validate(self) -> None:
        """Validate configuration settings."""
        
        # Validate proxy configuration
        if self.proxy_config.enabled:
            if self.proxy_config.rotation_interval < 60:
                raise ValueError("Proxy rotation interval must be at least 60 seconds")
            
            if self.proxy_config.max_requests_per_proxy < 1:
                raise ValueError("Max requests per proxy must be at least 1")
        
        # Validate search configuration  
        if self.search_config.timeout < 5:
            raise ValueError("Search timeout must be at least 5 seconds")
            
        if self.search_config.max_retries < 0:
            raise ValueError("Max retries cannot be negative")
            
        if not (0.0 <= self.search_config.fuzzy_threshold <= 1.0):
            raise ValueError("Fuzzy threshold must be between 0.0 and 1.0")
        
        # Validate cache configuration
        if self.cache_config.enabled:
            if self.cache_config.ttl < 60:
                raise ValueError("Cache TTL must be at least 60 seconds")
                
            if self.cache_config.max_size < 1:
                raise ValueError("Cache max size must be at least 1")
        
        # Validate rate limiting
        if self.search_config.requests_per_minute < 1:
            raise ValueError("Requests per minute must be at least 1")
            
        if self.search_config.burst_allowance < self.search_config.requests_per_minute:
            raise ValueError("Burst allowance must be >= requests per minute")
    
    def create_directories(self) -> None:
        """Create necessary directories."""
        
        if self.cache_config.enabled:
            self.cache_config.cache_dir.mkdir(parents=True, exist_ok=True)
            
        if self.logging_config.file_enabled:
            self.logging_config.log_dir.mkdir(parents=True, exist_ok=True)