# Installation Guide

This guide will walk you through installing and setting up the ICE Locator MCP Server on your system.

## System Requirements

### Minimum Requirements
- **Python**: 3.10 or higher
- **RAM**: 512 MB available memory
- **Storage**: 100 MB free disk space
- **Network**: Internet connection for ICE data access

### Recommended Requirements
- **Python**: 3.11 or 3.12
- **RAM**: 2 GB available memory
- **Storage**: 1 GB free disk space (for caching)
- **Network**: Stable broadband connection

### Supported Operating Systems
- **Linux**: Ubuntu 20.04+, CentOS 8+, Debian 11+
- **macOS**: 10.15 (Catalina) or higher
- **Windows**: Windows 10 or higher with WSL2 (recommended) or native Python

## Installation Methods

### Method 1: Install from PyPI (Recommended)

```bash
# Install via pip
pip install ice-locator-mcp

# Verify installation
ice-locator-mcp --version
```

### Method 2: Install from Source

```bash
# Clone the repository
git clone https://github.com/trose/ice-locator-mcp.git
cd ice-locator-mcp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# Verify installation
python -m ice_locator_mcp --version
```

### Method 3: Install with Development Dependencies

```bash
# Clone and setup for development
git clone https://github.com/trose/ice-locator-mcp.git
cd ice-locator-mcp

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install with development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests to verify
pytest
```

## Configuration

### Basic Configuration

Create a configuration file at `~/.config/ice-locator-mcp/config.json`:

```json
{
  "server": {
    "host": "localhost",
    "port": 8000,
    "debug": false
  },
  "rate_limiting": {
    "enabled": true,
    "requests_per_minute": 10,
    "burst_allowance": 20
  },
  "caching": {
    "enabled": true,
    "ttl": 3600,
    "cache_dir": "~/.cache/ice-locator-mcp"
  },
  "logging": {
    "level": "INFO",
    "file": "~/.logs/ice-locator-mcp.log"
  }
}
```

### Environment Variables

Set these environment variables for configuration:

```bash
# Basic configuration
export ICE_LOCATOR_CONFIG="/path/to/config.json"
export ICE_LOCATOR_LOG_LEVEL="INFO"
export ICE_LOCATOR_CACHE_DIR="~/.cache/ice-locator-mcp"

# Rate limiting
export ICE_LOCATOR_RATE_LIMIT="10"
export ICE_LOCATOR_BURST_ALLOWANCE="20"

# Advanced settings
export ICE_LOCATOR_PROXY_ENABLED="true"
export ICE_LOCATOR_DEBUG="false"
```

### Proxy Configuration (Optional)

For enhanced anti-detection, configure proxy settings:

```json
{
  "proxy": {
    "enabled": true,
    "rotation_interval": 1800,
    "health_check_interval": 300,
    "proxy_list_file": "~/.config/ice-locator-mcp/proxies.txt"
  }
}
```

Create `proxies.txt` with proxy list:
```
proxy1.example.com:8080:username:password
proxy2.example.com:8080
socks5://proxy3.example.com:1080
```

## MCP Client Setup

### Claude Desktop Integration

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "ice-locator": {
      "command": "ice-locator-mcp",
      "args": [],
      "env": {
        "ICE_LOCATOR_CONFIG": "/Users/yourusername/.config/ice-locator-mcp/config.json"
      }
    }
  }
}
```

### VS Code with MCP Extension

1. Install the MCP extension for VS Code
2. Add server configuration in VS Code settings:

```json
{
  "mcp.servers": {
    "ice-locator": {
      "command": "ice-locator-mcp",
      "args": [],
      "cwd": "${workspaceFolder}"
    }
  }
}
```

### Custom Python Client

```python
#!/usr/bin/env python3
"""
Example Python client for ICE Locator MCP Server
"""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    # Server configuration
    server_params = StdioServerParameters(
        command="ice-locator-mcp",
        args=[],
        env={"ICE_LOCATOR_CONFIG": "/path/to/config.json"}
    )
    
    # Connect to server
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize connection
            await session.initialize()
            
            # List available tools
            tools = await session.list_tools()
            print("Available tools:", [tool.name for tool in tools])
            
            # Search by name example
            result = await session.call_tool(
                "search_by_name",
                {
                    "first_name": "John",
                    "last_name": "Doe",
                    "fuzzy_match": True
                }
            )
            
            print("Search result:", result.content[0].text)

if __name__ == "__main__":
    asyncio.run(main())
```

## First Run

### Test Installation

```bash
# Test basic functionality
ice-locator-mcp --help

# Test server startup
ice-locator-mcp --test-connection

# Run in debug mode
ice-locator-mcp --debug
```

### Validate Configuration

```bash
# Check configuration
ice-locator-mcp --validate-config

# Test proxy settings (if configured)
ice-locator-mcp --test-proxies

# Check rate limiting
ice-locator-mcp --test-rate-limits
```

### Example Search

```bash
# Simple name search
ice-locator-mcp search --name "John Doe"

# A-Number search
ice-locator-mcp search --alien-number "A123456789"

# Facility search
ice-locator-mcp search --facility "Houston Contract Detention Facility"
```

## Docker Installation

### Using Docker Hub

```bash
# Pull the image
docker pull trose/ice-locator-mcp:latest

# Run the container
docker run -d \
  --name ice-locator-mcp \
  -p 8000:8000 \
  -v ~/.config/ice-locator-mcp:/config \
  -v ~/.cache/ice-locator-mcp:/cache \
  trose/ice-locator-mcp:latest
```

### Build from Source

```bash
# Clone repository
git clone https://github.com/trose/ice-locator-mcp.git
cd ice-locator-mcp

# Build Docker image
docker build -t ice-locator-mcp .

# Run with custom configuration
docker run -d \
  --name ice-locator-mcp \
  -p 8000:8000 \
  -v $(pwd)/config:/config \
  -v $(pwd)/cache:/cache \
  ice-locator-mcp
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  ice-locator-mcp:
    image: trose/ice-locator-mcp:latest
    ports:
      - "8000:8000"
    volumes:
      - ./config:/config
      - ./cache:/cache
      - ./logs:/logs
    environment:
      - ICE_LOCATOR_CONFIG=/config/config.json
      - ICE_LOCATOR_LOG_LEVEL=INFO
    restart: unless-stopped
    
  # Optional: Add a reverse proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - ice-locator-mcp
```

Run with:
```bash
docker-compose up -d
```

## Verification

### Health Check

```bash
# Check server health
curl http://localhost:8000/health

# Expected response:
# {"status": "healthy", "version": "0.1.0", "uptime": "0:05:23"}
```

### Test MCP Connection

```bash
# Test MCP protocol
echo '{"jsonrpc": "2.0", "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}}, "id": 1}' | ice-locator-mcp
```

### Sample Search Test

```python
#!/usr/bin/env python3
"""
Installation verification script
"""

import asyncio
import subprocess
import sys

async def verify_installation():
    try:
        # Test basic import
        import ice_locator_mcp
        print("✓ Package import successful")
        
        # Test server startup
        result = subprocess.run([
            sys.executable, "-m", "ice_locator_mcp", "--version"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print(f"✓ Server startup successful: {result.stdout.strip()}")
        else:
            print(f"✗ Server startup failed: {result.stderr}")
            return False
            
        # Test configuration
        from ice_locator_mcp.core.config import Config
        config = Config()
        print("✓ Configuration loaded successfully")
        
        # Test basic functionality
        from ice_locator_mcp.tools.search_tools import SearchTools
        search_tools = SearchTools(None)
        print("✓ Search tools initialized")
        
        print("\n🎉 Installation verification completed successfully!")
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Verification failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(verify_installation())
    sys.exit(0 if success else 1)
```

## Troubleshooting

### Common Issues

**Python Version Error:**
```bash
# Check Python version
python --version

# If using Python 3.10+, but still getting errors:
python3.11 -m pip install ice-locator-mcp
```

**Permission Errors:**
```bash
# Use user installation
pip install --user ice-locator-mcp

# Or fix permissions
sudo chown -R $USER ~/.local
```

**Import Errors:**
```bash
# Clear pip cache
pip cache purge

# Reinstall in clean environment
pip uninstall ice-locator-mcp
pip install ice-locator-mcp
```

**Configuration Not Found:**
```bash
# Create config directory
mkdir -p ~/.config/ice-locator-mcp

# Copy default configuration
ice-locator-mcp --create-default-config
```

### Getting Help

1. **Check logs**: `~/.logs/ice-locator-mcp.log`
2. **Run diagnostics**: `ice-locator-mcp --diagnose`
3. **Community support**: [GitHub Discussions](https://github.com/trose/ice-locator-mcp/discussions)
4. **Report bugs**: [GitHub Issues](https://github.com/trose/ice-locator-mcp/issues)

## Next Steps

After successful installation:

1. Review the [Configuration Guide](configuration.md)
2. Read the [Usage Examples](examples.md)
3. Check the [API Documentation](api.md)
4. Explore [Advanced Features](advanced.md)
5. Review [Legal Guidelines](legal.md)

## Uninstallation

### Remove Package

```bash
# Uninstall via pip
pip uninstall ice-locator-mcp

# Remove configuration and cache
rm -rf ~/.config/ice-locator-mcp
rm -rf ~/.cache/ice-locator-mcp
rm -rf ~/.logs/ice-locator-mcp.log
```

### Clean Docker Installation

```bash
# Stop and remove containers
docker-compose down

# Remove images
docker rmi trose/ice-locator-mcp:latest

# Clean volumes
docker volume prune
```