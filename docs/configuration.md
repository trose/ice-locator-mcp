# Configuration Guide

This guide covers all configuration options for the ICE Locator MCP Server.

## Configuration File Location

The configuration file can be placed in several locations (checked in order):

1. `ICE_LOCATOR_CONFIG` environment variable path
2. `~/.config/ice-locator-mcp/config.json`
3. `./config/config.json` (relative to working directory)
4. Built-in defaults

## Configuration Format

The configuration file uses JSON format with the following structure:

```json
{
  "server": {
    "host": "localhost",
    "port": 8000,
    "debug": false,
    "log_level": "INFO"
  },
  "rate_limiting": {
    "enabled": true,
    "requests_per_minute": 10,
    "burst_allowance": 20,
    "adaptive": true
  },
  "caching": {
    "enabled": true,
    "ttl": 3600,
    "cache_dir": "~/.cache/ice-locator-mcp",
    "max_size_mb": 100
  },
  "proxy": {
    "enabled": false,
    "rotation_interval": 1800,
    "health_check_interval": 300,
    "proxy_list_file": null
  },
  "scraper": {
    "base_url": "https://locator.ice.gov",
    "timeout": 30,
    "retries": 3,
    "user_agent_rotation": true
  },
  "privacy": {
    "data_minimization": true,
    "anonymization": true,
    "retention_days": 30
  },
  "compliance": {
    "audit_logging": true,
    "data_retention_days": 30,
    "privacy_mode": true
  },
  "logging": {
    "level": "INFO",
    "file": "~/.logs/ice-locator-mcp.log",
    "max_size_mb": 10,
    "backup_count": 5
  }
}
```

## Configuration Sections

### Server Configuration

Controls basic server behavior:

```json
{
  "server": {
    "host": "localhost",
    "port": 8000,
    "debug": false,
    "log_level": "INFO",
    "workers": 1,
    "max_connections": 100
  }
}
```

**Options:**
- `host`: Server bind address (default: "localhost")
- `port`: Server port (default: 8000)
- `debug`: Enable debug mode (default: false)
- `log_level`: Logging level ("DEBUG", "INFO", "WARNING", "ERROR")
- `workers`: Number of worker processes (default: 1)
- `max_connections`: Maximum concurrent connections (default: 100)

### Rate Limiting

Prevents abuse and manages request rates:

```json
{
  "rate_limiting": {
    "enabled": true,
    "requests_per_minute": 10,
    "burst_allowance": 20,
    "adaptive": true,
    "per_ip_limit": 5,
    "global_limit": 100
  }
}
```

**Options:**
- `enabled`: Enable rate limiting (default: true)
- `requests_per_minute`: Base rate limit (default: 10)
- `burst_allowance`: Burst capacity (default: 20)
- `adaptive`: Adjust rates based on success/error ratios (default: true)
- `per_ip_limit`: Per-IP rate limit (default: 5)
- `global_limit`: Global rate limit across all clients (default: 100)

### Caching

Controls result caching behavior:

```json
{
  "caching": {
    "enabled": true,
    "ttl": 3600,
    "cache_dir": "~/.cache/ice-locator-mcp",
    "max_size_mb": 100,
    "cleanup_interval": 3600,
    "compression": true
  }
}
```

**Options:**
- `enabled`: Enable caching (default: true)
- `ttl`: Time-to-live in seconds (default: 3600)
- `cache_dir`: Cache directory path
- `max_size_mb`: Maximum cache size in MB (default: 100)
- `cleanup_interval`: Cleanup interval in seconds (default: 3600)
- `compression`: Compress cached data (default: true)

### Proxy Configuration

For enhanced anti-detection:

```json
{
  "proxy": {
    "enabled": true,
    "rotation_interval": 1800,
    "health_check_interval": 300,
    "proxy_list_file": "~/.config/ice-locator-mcp/proxies.txt",
    "proxy_timeout": 10,
    "max_retries": 3,
    "fallback_to_direct": true
  }
}
```

**Options:**
- `enabled`: Enable proxy usage (default: false)
- `rotation_interval`: Proxy rotation interval in seconds (default: 1800)
- `health_check_interval`: Health check interval in seconds (default: 300)
- `proxy_list_file`: Path to proxy list file
- `proxy_timeout`: Proxy connection timeout (default: 10)
- `max_retries`: Maximum proxy retry attempts (default: 3)
- `fallback_to_direct`: Fall back to direct connection if all proxies fail

#### Proxy List Format

Create a text file with one proxy per line:

```
# HTTP/HTTPS proxies
http://proxy1.example.com:8080
https://user:pass@proxy2.example.com:8080

# SOCKS proxies
socks4://proxy3.example.com:1080
socks5://user:pass@proxy4.example.com:1080

# Proxy with metadata (optional)
http://proxy5.example.com:8080#residential,us
```

### Scraper Configuration

Controls web scraping behavior:

```json
{
  "scraper": {
    "base_url": "https://locator.ice.gov",
    "timeout": 30,
    "retries": 3,
    "user_agent_rotation": true,
    "respect_robots_txt": true,
    "delay_between_requests": 1.0,
    "max_concurrent_requests": 5
  }
}
```

**Options:**
- `base_url`: ICE locator website URL (default: "https://locator.ice.gov")
- `timeout`: Request timeout in seconds (default: 30)
- `retries`: Maximum retry attempts (default: 3)
- `user_agent_rotation`: Rotate user agents (default: true)
- `respect_robots_txt`: Respect robots.txt (default: true)
- `delay_between_requests`: Delay between requests in seconds (default: 1.0)
- `max_concurrent_requests`: Maximum concurrent requests (default: 5)

### Privacy Settings

Controls privacy and data protection:

```json
{
  "privacy": {
    "data_minimization": true,
    "anonymization": true,
    "retention_days": 30,
    "encrypt_cache": false,
    "redact_logs": true,
    "secure_delete": true
  }
}
```

**Options:**
- `data_minimization`: Minimize data collection (default: true)
- `anonymization`: Anonymize cached data (default: true)
- `retention_days`: Data retention period (default: 30)
- `encrypt_cache`: Encrypt cached data (default: false)
- `redact_logs`: Redact sensitive information in logs (default: true)
- `secure_delete`: Securely delete expired data (default: true)

### Compliance Settings

Legal and regulatory compliance:

```json
{
  "compliance": {
    "audit_logging": true,
    "data_retention_days": 30,
    "privacy_mode": true,
    "gdpr_compliance": true,
    "ccpa_compliance": true,
    "foia_compliance": true
  }
}
```

### Logging Configuration

Controls logging behavior:

```json
{
  "logging": {
    "level": "INFO",
    "file": "~/.logs/ice-locator-mcp.log",
    "max_size_mb": 10,
    "backup_count": 5,
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "console_output": true,
    "structured_logs": true
  }
}
```

## Environment Variables

All configuration options can be overridden using environment variables:

```bash
# Server configuration
export ICE_LOCATOR_HOST="0.0.0.0"
export ICE_LOCATOR_PORT="8080"
export ICE_LOCATOR_DEBUG="true"

# Rate limiting
export ICE_LOCATOR_RATE_LIMIT="15"
export ICE_LOCATOR_BURST_ALLOWANCE="30"

# Caching
export ICE_LOCATOR_CACHE_ENABLED="true"
export ICE_LOCATOR_CACHE_TTL="7200"
export ICE_LOCATOR_CACHE_DIR="/custom/cache/dir"

# Proxy settings
export ICE_LOCATOR_PROXY_ENABLED="true"
export ICE_LOCATOR_PROXY_LIST="/path/to/proxies.txt"

# Privacy settings
export ICE_LOCATOR_PRIVACY_MODE="true"
export ICE_LOCATOR_DATA_RETENTION="14"

# Logging
export ICE_LOCATOR_LOG_LEVEL="DEBUG"
export ICE_LOCATOR_LOG_FILE="/var/log/ice-locator-mcp.log"
```

## Configuration Validation

Validate your configuration before starting:

```bash
# Validate configuration file
ice-locator-mcp --validate-config

# Test configuration with dry run
ice-locator-mcp --dry-run

# Show effective configuration
ice-locator-mcp --show-config
```

## Advanced Configuration

### Custom User Agent Lists

Create custom user agent rotation:

```json
{
  "scraper": {
    "user_agents": [
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
      "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
    ]
  }
}
```

### Custom Headers

Add custom headers to requests:

```json
{
  "scraper": {
    "custom_headers": {
      "Accept-Language": "en-US,en;q=0.9",
      "Accept-Encoding": "gzip, deflate, br",
      "DNT": "1"
    }
  }
}
```

### Performance Tuning

Optimize for your use case:

```json
{
  "performance": {
    "connection_pool_size": 20,
    "connection_pool_maxsize": 20,
    "tcp_keepalive": true,
    "http2": false,
    "compression": true
  }
}
```

### Security Hardening

Enhanced security settings:

```json
{
  "security": {
    "enable_ssl_verification": true,
    "cipher_suites": ["TLS_AES_256_GCM_SHA384", "TLS_CHACHA20_POLY1305_SHA256"],
    "min_tls_version": "1.2",
    "disable_weak_ciphers": true,
    "certificate_pinning": false
  }
}
```

## Configuration Examples

### Development Environment

```json
{
  "server": {
    "debug": true,
    "log_level": "DEBUG"
  },
  "rate_limiting": {
    "requests_per_minute": 60,
    "burst_allowance": 100
  },
  "caching": {
    "ttl": 300
  },
  "proxy": {
    "enabled": false
  }
}
```

### Production Environment

```json
{
  "server": {
    "debug": false,
    "log_level": "INFO",
    "workers": 4
  },
  "rate_limiting": {
    "requests_per_minute": 10,
    "burst_allowance": 20,
    "adaptive": true
  },
  "caching": {
    "ttl": 3600,
    "max_size_mb": 500
  },
  "proxy": {
    "enabled": true,
    "rotation_interval": 900
  },
  "privacy": {
    "data_minimization": true,
    "anonymization": true,
    "encrypt_cache": true
  }
}
```

### High-Volume Environment

```json
{
  "server": {
    "workers": 8,
    "max_connections": 500
  },
  "rate_limiting": {
    "requests_per_minute": 30,
    "burst_allowance": 100,
    "per_ip_limit": 10
  },
  "caching": {
    "ttl": 7200,
    "max_size_mb": 1000,
    "compression": true
  },
  "performance": {
    "connection_pool_size": 50,
    "connection_pool_maxsize": 50
  }
}
```

## Configuration Migration

### From Version 0.1.x to 0.2.x

```bash
# Backup existing configuration
cp ~/.config/ice-locator-mcp/config.json ~/.config/ice-locator-mcp/config.json.backup

# Run migration tool
ice-locator-mcp --migrate-config

# Validate migrated configuration
ice-locator-mcp --validate-config
```

## Troubleshooting Configuration

### Common Issues

**Configuration not found:**
```bash
# Check configuration search paths
ice-locator-mcp --config-paths

# Create default configuration
ice-locator-mcp --create-default-config
```

**Invalid JSON:**
```bash
# Validate JSON syntax
python -m json.tool ~/.config/ice-locator-mcp/config.json

# Use configuration validator
ice-locator-mcp --validate-config --verbose
```

**Permission errors:**
```bash
# Fix directory permissions
chmod 755 ~/.config/ice-locator-mcp
chmod 644 ~/.config/ice-locator-mcp/config.json

# Check cache directory permissions
ls -la ~/.cache/ice-locator-mcp
```

### Configuration Debugging

Enable configuration debugging:

```bash
# Show configuration loading process
ICE_LOCATOR_DEBUG_CONFIG=true ice-locator-mcp --show-config

# Trace configuration sources
ice-locator-mcp --trace-config
```

## Security Considerations

1. **File Permissions**: Ensure configuration files have appropriate permissions (644 or 600)
2. **Sensitive Data**: Never store passwords or API keys in plain text
3. **Environment Variables**: Use environment variables for sensitive configuration
4. **Configuration Validation**: Always validate configuration before deployment
5. **Regular Updates**: Keep configuration updated with security best practices