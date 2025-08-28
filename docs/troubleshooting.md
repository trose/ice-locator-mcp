# Troubleshooting Guide

This guide helps resolve common issues when using the ICE Locator MCP Server.

## Installation Issues

### Python Version Compatibility

**Problem**: `ice-locator-mcp` fails to install or run
```
ERROR: ice-locator-mcp requires Python '>=3.10' but the running Python is 3.9.x
```

**Solution**:
```bash
# Check Python version
python --version

# Install Python 3.10+ using pyenv
curl https://pyenv.run | bash
pyenv install 3.11.7
pyenv global 3.11.7

# Or use system package manager
# Ubuntu/Debian
sudo apt update && sudo apt install python3.11

# macOS
brew install python@3.11

# Verify installation
python3.11 --version
python3.11 -m pip install ice-locator-mcp
```

### Permission Errors

**Problem**: Permission denied during installation
```
ERROR: Could not install packages due to an OSError: [Errno 13] Permission denied
```

**Solution**:
```bash
# Use user installation
pip install --user ice-locator-mcp

# Or fix pip permissions
python -m pip install --upgrade pip
pip install ice-locator-mcp

# On Linux/macOS, avoid sudo with pip
# Instead use virtual environments
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install ice-locator-mcp
```

### Import Errors

**Problem**: Module not found after installation
```
ModuleNotFoundError: No module named 'ice_locator_mcp'
```

**Solution**:
```bash
# Check if package is installed
pip show ice-locator-mcp

# Verify installation location
python -c "import sys; print(sys.path)"

# Reinstall in current environment
pip uninstall ice-locator-mcp
pip install ice-locator-mcp

# Check Python environment
which python
which pip
```

## Configuration Issues

### Configuration File Not Found

**Problem**: Server can't find configuration file
```
WARNING: Configuration file not found, using defaults
```

**Solution**:
```bash
# Create default configuration
ice-locator-mcp --create-default-config

# Set configuration path
export ICE_LOCATOR_CONFIG="/path/to/config.json"

# Check configuration search paths
ice-locator-mcp --config-paths

# Verify configuration is valid
ice-locator-mcp --validate-config
```

### Invalid Configuration Format

**Problem**: Configuration file has syntax errors
```
ERROR: Invalid JSON in configuration file
```

**Solution**:
```bash
# Validate JSON syntax
python -m json.tool ~/.config/ice-locator-mcp/config.json

# Check for common issues
cat ~/.config/ice-locator-mcp/config.json | grep -E '[{}"\[\]]'

# Use configuration validator
ice-locator-mcp --validate-config --verbose

# Reset to defaults if corrupted
mv ~/.config/ice-locator-mcp/config.json ~/.config/ice-locator-mcp/config.json.backup
ice-locator-mcp --create-default-config
```

## Connection Issues

### MCP Server Won't Start

**Problem**: Server fails to start or connect
```
ERROR: Failed to start MCP server
```

**Diagnosis**:
```bash
# Check if server starts manually
ice-locator-mcp --test-connection

# Run in debug mode
ICE_LOCATOR_LOG_LEVEL=DEBUG ice-locator-mcp

# Check for port conflicts
netstat -tuln | grep 8000
lsof -i :8000

# Verify dependencies
pip check
```

**Solution**:
```bash
# Kill conflicting processes
pkill -f ice-locator-mcp

# Use different port
export ICE_LOCATOR_PORT=8001

# Check file permissions
ls -la ~/.config/ice-locator-mcp/
chmod 755 ~/.config/ice-locator-mcp/
chmod 644 ~/.config/ice-locator-mcp/config.json

# Reinstall if corrupted
pip uninstall ice-locator-mcp
pip install --no-cache-dir ice-locator-mcp
```

### Proxy Connection Failures

**Problem**: Proxy connections are failing
```
ERROR: All proxy connections failed
```

**Solution**:
```bash
# Test proxy connectivity
curl --proxy http://proxy:port http://httpbin.org/ip

# Disable proxy temporarily
export ICE_LOCATOR_PROXY_ENABLED=false

# Check proxy configuration
ice-locator-mcp --test-proxies

# Verify proxy list format
cat ~/.config/ice-locator-mcp/proxies.txt

# Reset proxy health status
ice-locator-mcp --reset-proxy-health
```

## Search Issues

### No Results Found

**Problem**: Searches return no results for known data
```
{"status": "not_found", "results": []}
```

**Diagnosis**:
```bash
# Enable fuzzy matching
{
  "first_name": "John",
  "last_name": "Doe", 
  "fuzzy_match": true,
  "confidence_threshold": 0.6
}

# Check for spelling variations
# Try different name formats
# Verify A-number format (with/without 'A' prefix)
```

**Solution**:
- Lower confidence threshold for fuzzy matching
- Try alternative spellings or transliterations
- Use partial names if full names don't work
- Check if information is actually in the ICE database
- Verify name format (order, capitalization)

### Rate Limiting Issues

**Problem**: Requests are being rate limited
```
ERROR: Rate limit exceeded. Please wait before making another request.
```

**Solution**:
```bash
# Check current rate limits
ice-locator-mcp --show-rate-limits

# Adjust rate limiting configuration
{
  "rate_limiting": {
    "requests_per_minute": 5,
    "burst_allowance": 10
  }
}

# Wait for rate limit reset
# Use bulk search for multiple queries
# Enable proxy rotation to distribute requests
```

### CAPTCHA Challenges

**Problem**: CAPTCHA challenges are blocking searches
```
WARNING: CAPTCHA challenge detected, retrying with delay
```

**Solution**:
```bash
# Enable automatic CAPTCHA handling
{
  "captcha": {
    "auto_solve": true,
    "solver_service": "2captcha",  # Optional
    "max_attempts": 3
  }
}

# Reduce request frequency
{
  "rate_limiting": {
    "requests_per_minute": 3,
    "adaptive": true
  }
}

# Enable behavioral simulation
{
  "anti_detection": {
    "human_simulation": true,
    "random_delays": true
  }
}
```

## Performance Issues

### Slow Response Times

**Problem**: Searches are taking too long
```
Search completed in 15.2 seconds (expected < 5 seconds)
```

**Diagnosis**:
```bash
# Check network latency
ping locator.ice.gov

# Test direct connection vs proxy
ice-locator-mcp --benchmark --no-proxy
ice-locator-mcp --benchmark --with-proxy

# Monitor resource usage
top -p $(pgrep ice-locator-mcp)
```

**Solutions**:
```bash
# Optimize configuration
{
  "scraper": {
    "timeout": 10,
    "max_concurrent_requests": 3
  },
  "caching": {
    "enabled": true,
    "ttl": 3600
  }
}

# Use faster proxies
# Enable caching
# Reduce timeout values
# Use bulk search for multiple queries
```

### Memory Usage Issues

**Problem**: High memory consumption
```
WARNING: Memory usage above 500MB
```

**Solution**:
```bash
# Enable cache cleanup
{
  "caching": {
    "max_size_mb": 100,
    "cleanup_interval": 1800
  }
}

# Reduce cache TTL
{
  "caching": {
    "ttl": 1800  # 30 minutes instead of 1 hour
  }
}

# Monitor memory usage
ice-locator-mcp --memory-stats

# Restart server periodically in long-running applications
```

## Network Issues

### SSL/TLS Errors

**Problem**: SSL certificate verification failures
```
SSLError: certificate verify failed
```

**Solution**:
```bash
# Update certificates
pip install --upgrade certifi

# Check system time (important for SSL)
date

# Verify SSL configuration
{
  "security": {
    "enable_ssl_verification": true,
    "min_tls_version": "1.2"
  }
}

# For testing only (NOT for production):
export PYTHONHTTPSVERIFY=0
```

### DNS Resolution Issues

**Problem**: Cannot resolve locator.ice.gov
```
gaierror: [Errno -2] Name or service not known
```

**Solution**:
```bash
# Test DNS resolution
nslookup locator.ice.gov
dig locator.ice.gov

# Use different DNS servers
echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# Check network connectivity
ping 8.8.8.8
curl -I https://locator.ice.gov

# Use IP address if DNS fails (temporary)
```

## Cache Issues

### Cache Corruption

**Problem**: Corrupted cache data causing errors
```
ERROR: Failed to deserialize cached data
```

**Solution**:
```bash
# Clear cache
ice-locator-mcp --clear-cache

# Or manually remove cache directory
rm -rf ~/.cache/ice-locator-mcp/

# Disable cache temporarily
export ICE_LOCATOR_CACHE_ENABLED=false

# Check cache directory permissions
ls -la ~/.cache/ice-locator-mcp/
```

### Cache Size Issues

**Problem**: Cache consuming too much disk space
```
WARNING: Cache size exceeds maximum limit
```

**Solution**:
```bash
# Check cache size
du -sh ~/.cache/ice-locator-mcp/

# Configure cache limits
{
  "caching": {
    "max_size_mb": 50,
    "cleanup_interval": 900
  }
}

# Force cache cleanup
ice-locator-mcp --cleanup-cache
```

## Logging and Debugging

### Enable Debug Logging

```bash
# Set debug log level
export ICE_LOCATOR_LOG_LEVEL=DEBUG

# Or in configuration
{
  "logging": {
    "level": "DEBUG",
    "file": "~/.logs/ice-locator-mcp-debug.log"
  }
}

# Run with verbose output
ice-locator-mcp --verbose
```

### Collect Diagnostic Information

```bash
# Generate diagnostic report
ice-locator-mcp --diagnose > diagnostic-report.txt

# Include system information
ice-locator-mcp --system-info

# Check dependencies
pip list | grep -E "(ice-locator|mcp|httpx|beautifulsoup)"

# Test configuration
ice-locator-mcp --test-config
```

## Common Error Messages

### "Connection refused"
- Server not running or wrong port
- Firewall blocking connection
- Check server status and port configuration

### "Invalid JSON response"
- Network connectivity issues
- Server returning HTML error pages
- Enable debug logging to see raw responses

### "Module 'ice_locator_mcp' has no attribute"
- Version mismatch between client and server
- Incomplete installation
- Reinstall package

### "Permission denied"
- File permission issues
- Directory access problems
- Fix with `chmod` and `chown`

### "Timeout waiting for response"
- Network latency issues
- Server overload
- Increase timeout values

## Getting Help

### Collecting Information for Bug Reports

```bash
# System information
ice-locator-mcp --version
python --version
pip show ice-locator-mcp

# Configuration (redacted)
ice-locator-mcp --show-config --redact-sensitive

# Recent logs
tail -50 ~/.logs/ice-locator-mcp.log

# Diagnostic report
ice-locator-mcp --diagnose --include-config
```

### Support Channels

1. **GitHub Issues**: For bugs and feature requests
   - Include diagnostic information
   - Provide minimal reproduction steps
   - Redact sensitive information

2. **GitHub Discussions**: For questions and help
   - Search existing discussions first
   - Provide context about your use case

3. **Documentation**: Check all docs before asking
   - API documentation
   - Configuration guide
   - Examples and tutorials

### Temporary Workarounds

While waiting for fixes, these workarounds may help:

1. **Rate limiting issues**: Reduce request frequency
2. **Memory issues**: Restart server periodically  
3. **Cache issues**: Disable caching temporarily
4. **Proxy issues**: Use direct connections
5. **SSL issues**: Use HTTP for testing (not production)

Remember to remove workarounds once proper fixes are available.