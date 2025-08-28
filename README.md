# 🔍 ICE Locator MCP Server

[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-brightgreen)](https://modelcontextprotocol.io)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/trose/ice-locator-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/trose/ice-locator-mcp/actions)
[![Coverage](https://codecov.io/gh/trose/ice-locator-mcp/branch/main/graph/badge.svg)](https://codecov.io/gh/trose/ice-locator-mcp)

> **Empower AI agents with ICE detainee location capabilities**

Connect your LLM applications to the U.S. Immigration and Customs Enforcement (ICE) Online Detainee Locator System through a standardized Model Context Protocol (MCP) interface.

## ✨ Features

- 🔍 **Smart Search**: Natural language queries with fuzzy matching
- 🛡️ **Anti-Detection**: Advanced IP rotation and behavioral simulation  
- 📊 **Bulk Operations**: Search multiple detainees simultaneously
- 🌐 **Multilingual**: Support for English, Spanish, and more
- 📋 **Legal Reports**: Generate comprehensive reports for legal use
- 🔒 **Privacy-First**: Local processing with optional caching
- ⚡ **High Performance**: Async operations with intelligent rate limiting
- 🎯 **AI-Powered**: Enhanced search with auto-corrections and suggestions

## 🚀 Quick Start

### Installation

```bash
# Install via pip
pip install ice-locator-mcp

# Or install from source
git clone https://github.com/trose/ice-locator-mcp.git
cd ice-locator-mcp
pip install -e .
```

### Configuration for Claude Desktop

Add to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "ice-locator": {
      "command": "ice-locator-mcp",
      "args": []
    }
  }
}
```

### Configuration for Cursor IDE

Add to your Cursor settings:

```json
{
  "mcp.servers": [
    {
      "name": "ice-locator",
      "command": "ice-locator-mcp"
    }
  ]
}
```

## 📖 Usage Examples

### Basic Name Search

```python
# Search by name and personal information
result = await search_detainee_by_name(
    first_name="John",
    last_name="Doe", 
    date_of_birth="1990-01-15",
    country_of_birth="Mexico"
)
```

### Natural Language Search

```python
# AI-powered natural language search
result = await smart_detainee_search(
    query="Find Maria Rodriguez from Guatemala born around 1985"
)
```

### Bulk Search Operations

```python
# Search multiple detainees simultaneously
result = await bulk_search_detainees(
    search_requests=[
        {
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": "1990-01-15", 
            "country_of_birth": "Mexico"
        },
        {
            "alien_number": "A123456789"
        }
    ],
    max_concurrent=3
)
```

### Generate Legal Reports

```python
# Create comprehensive reports for legal use
result = await generate_search_report(
    search_criteria={"first_name": "John", "last_name": "Doe"},
    results=[...],
    report_type="legal",
    format="markdown"
)
```

## 🎯 Use Cases

### Legal Representatives
- Quickly locate clients in ICE custody
- Generate comprehensive case reports
- Track custody status changes
- Access facility and contact information

### Family Members  
- Find detained relatives with AI assistance
- Understand next steps and resources
- Get visiting information and guidelines
- Access family support resources

### Advocacy Organizations
- Streamline detainee location workflows
- Bulk search capabilities for case management
- Generate reports for advocacy efforts
- Monitor detention patterns and trends

### AI Assistants
- Enable immigration-related support capabilities
- Provide intelligent search recommendations
- Offer multilingual assistance
- Guide users through complex processes

## 🛡️ Anti-Detection Features

### IP Rotation & Proxy Management
- Automatic IP rotation with health monitoring
- Geographic distribution of requests
- Residential proxy preference
- Intelligent failover and recovery

### Behavioral Simulation
- Human-like browsing patterns
- Realistic timing and delays
- Form interaction simulation
- Session management

### Request Obfuscation
- Randomized browser fingerprints
- Header rotation and variation
- Traffic pattern obfuscation
- CAPTCHA handling strategies

## ⚙️ Configuration

### Environment Variables

```bash
# Proxy settings
export ICE_LOCATOR_PROXY_ENABLED=true
export ICE_LOCATOR_PROXY_ROTATION_INTERVAL=300

# Rate limiting
export ICE_LOCATOR_REQUESTS_PER_MINUTE=10
export ICE_LOCATOR_TIMEOUT=30

# Caching
export ICE_LOCATOR_CACHE_ENABLED=true
export ICE_LOCATOR_CACHE_TTL=3600
export ICE_LOCATOR_CACHE_DIR=~/.cache/ice-locator-mcp

# Logging
export ICE_LOCATOR_LOG_LEVEL=INFO
export ICE_LOCATOR_LOG_DIR=~/.logs/ice-locator-mcp
```

### Configuration File

Create `config.yml` in your working directory:

```yaml
proxy:
  enabled: true
  rotation_interval: 300
  max_requests_per_proxy: 10

search:
  timeout: 30
  max_retries: 3
  fuzzy_threshold: 0.7
  human_delays: true

cache:
  enabled: true
  ttl: 3600
  backend: diskcache

security:
  log_sensitive_data: false
  anonymize_logs: true
  encrypt_cache: false
```

## 🧪 Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/yourusername/ice-locator-mcp.git
cd ice-locator-mcp

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ice_locator_mcp --cov-report=html

# Run specific test categories
pytest tests/unit/         # Unit tests only
pytest tests/integration/  # Integration tests only
```

### Code Quality

```bash
# Lint code
ruff check src/ tests/
ruff format src/ tests/

# Type checking
mypy src/ice_locator_mcp/

# Security scanning
bandit -r src/
safety check
```

## 📚 API Reference

### Available Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `search_detainee_by_name` | Search by personal information | `first_name`, `last_name`, `date_of_birth`, `country_of_birth` |
| `search_detainee_by_alien_number` | Search by A-number | `alien_number` |
| `smart_detainee_search` | AI-powered natural language search | `query`, `context` |
| `bulk_search_detainees` | Multiple concurrent searches | `search_requests`, `max_concurrent` |
| `generate_search_report` | Create comprehensive reports | `search_criteria`, `results`, `report_type` |

### Response Schema

```json
{
  "status": "found|not_found|error|partial",
  "results": [
    {
      "alien_number": "A123456789",
      "name": "John Doe",
      "date_of_birth": "1990-01-15",
      "country_of_birth": "Mexico",
      "facility_name": "Processing Center",
      "facility_location": "City, State", 
      "custody_status": "In Custody",
      "last_updated": "2024-01-15T10:30:00Z",
      "confidence_score": 0.95
    }
  ],
  "search_metadata": {
    "search_date": "2024-01-15T10:30:00Z",
    "total_results": 1,
    "processing_time_ms": 1250,
    "corrections_applied": [],
    "suggestions": []
  },
  "user_guidance": {
    "next_steps": ["Contact facility", "Verify information"],
    "legal_resources": [],
    "family_resources": []
  }
}
```

## 🔒 Privacy & Security

### Data Handling
- **No Data Storage**: Search data is not permanently stored
- **Local Processing**: All processing happens locally
- **Optional Caching**: Cache can be disabled or encrypted
- **Anonymized Logs**: Sensitive information is anonymized in logs

### Responsible Usage
- **Legal Compliance**: Ensure compliance with applicable laws
- **Rate Limiting**: Respect ICE website rate limits
- **Ethical Use**: Use for legitimate purposes only
- **Privacy Protection**: Protect individual privacy and data

### Security Features
- **Encrypted Communication**: All requests use HTTPS
- **Secure Defaults**: Security-first configuration defaults  
- **Access Control**: No authentication required, but usage is monitored
- **Audit Logging**: Comprehensive logging for security audits

## 📜 Legal & Ethical Considerations

### Intended Use
This tool is designed for legitimate purposes including:
- Legal representation and advocacy
- Family reunification efforts
- Immigration support services
- Authorized research and journalism

### Restrictions
- Do not use for unauthorized surveillance
- Respect individual privacy rights
- Comply with applicable laws and regulations
- Do not overwhelm or abuse the ICE website

### Disclaimer
This software is provided for educational and legitimate use purposes. Users are responsible for ensuring their use complies with all applicable laws and regulations.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Process
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests and documentation
5. Submit a pull request

### Code of Conduct
Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing.

## 📋 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [Full Documentation](https://trose.github.io/ice-locator-mcp)
- **Issues**: [GitHub Issues](https://github.com/trose/ice-locator-mcp/issues)
- **Discussions**: [GitHub Discussions](https://github.com/trose/ice-locator-mcp/discussions)
- **Email**: your.email@example.com

---

**⚠️ Important Notice**: This is an independent project not affiliated with ICE or any government agency. Use responsibly and in compliance with all applicable laws.