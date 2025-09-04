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
- 🗺️ **Heatmap Visualization**: Interactive maps showing facility locations and detainee counts

## 🗺️ Heatmap Visualization

Visualize ICE facility locations and detainee distributions with our interactive heatmap feature:

- **Web Interface**: React-based map visualization with Leaflet.js
- **Mobile App**: Native mobile experience with React Native
- **Real-time Data**: Live facility information and detainee counts
- **Cross-Platform**: Consistent experience across web and mobile
- **Performance**: Client-side caching and efficient data loading

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

### Browser-Based Simulation (Playwright)
- Real browser engine for maximum realism
- JavaScript execution and rendering
- Advanced fingerprinting evasion
- Human-like mouse movements and interactions
- Automatic CAPTCHA handling strategies

### Request Obfuscation
- Randomized browser fingerprints
- Header rotation and variation
- Traffic pattern obfuscation
- CAPTCHA handling strategies

## 🔒 Privacy-First Analytics & Monitoring

### MCPcat Analytics Integration
This MCP server includes **optional** integration with [MCPcat](https://mcpcat.io), an analytics platform specifically designed for MCP servers. **Your privacy and security are our top priority:**

#### **Automatic Data Redaction** 🛡️
- **All sensitive user data is automatically redacted** before any analytics collection
- Personal information (names, A-numbers, birthdates) is stripped from analytics
- Search queries are sanitized to remove personally identifiable information
- Only anonymized usage patterns and performance metrics are collected

#### **What Data is Collected** 📊
- Tool usage frequencies (which tools are most used)
- Performance metrics (response times, success rates)
- Error patterns (for improving reliability)
- AI model interaction patterns (for optimizing AI compatibility)
- **NO personal search data or results**

#### **What Data is NOT Collected** ❌
- Detainee names, A-numbers, or personal information
- Search query content or parameters
- Search results or facility information
- User identification or tracking data
- Sensitive case information

#### **Privacy Controls** 🔐
```
# Disable analytics completely
export ICE_LOCATOR_ANALYTICS_ENABLED=false
```

#### **Benefits of Analytics** ✨
- **Improved Performance**: Data-driven optimizations for better search reliability
- **Enhanced AI Compatibility**: Better integration with different AI models
- **Bug Detection**: Early identification of issues affecting users
- **Feature Development**: Understanding which capabilities users need most

#### **Transparency Commitment** 📋
- All analytics code is open source and auditable
- Data redaction happens locally before transmission
- No data is sold or shared with third parties
- Analytics can be completely disabled at any time
- Detailed privacy policy available at [docs/privacy](docs/PRIVACY.md)

> **🔒 Security First**: MCPcat is designed by privacy advocates for privacy advocates. All data is encrypted in transit and at rest, with comprehensive redaction ensuring sensitive information never leaves your environment.

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
- **Analytics Redaction**: MCPcat analytics automatically redacts all sensitive data

### Responsible Usage
- **Legal Compliance**: Ensure compliance with applicable laws
- **Rate Limiting**: Respect ICE website rate limits
- **Ethical Use**: Use for legitimate purposes only
- **Privacy Protection**: Protect individual privacy and data
- **Analytics Transparency**: Optional analytics with full data redaction

### Security Features
- **Encrypted Communication**: All requests use HTTPS
- **Secure Defaults**: Security-first configuration defaults  
- **Access Control**: No authentication required, but usage is monitored
- **Audit Logging**: Comprehensive logging for security audits
- **Privacy-First Analytics**: Sensitive data redaction in all monitoring

### MCPcat Privacy Assurance
- **Automatic Redaction**: All personal information is removed before analytics
- **Local Sanitization**: Data cleaning happens on your machine
- **Open Source**: Analytics code is fully auditable
- **Disable Anytime**: Analytics can be turned off completely
- **No Tracking**: No user identification or personal data collection

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

# ICE Locator MCP - Heatmap View Implementation

## Project Overview
This repository contains the implementation of a heatmap view for the ICE Locator MCP system. The project adds visualization capabilities to show detainee locations across facilities through both web and mobile interfaces.

## Implementation Summary

### Phase 1: Database and Data Seeding ✅
- Created PostgreSQL database schema with Detainee, Facility, and DetaineeLocationHistory tables
- Implemented DatabaseManager with CRUD operations
- Developed data seeding scripts with realistic sample data
- Added comprehensive unit tests

### Phase 2: API Layer Development ✅
- Built FastAPI-based REST API for heatmap data
- Created endpoints for facilities, facility details, and heatmap visualization
- Implemented database integration with proper error handling
- Added unit and integration tests

### Phase 3: Web App Implementation ✅
- Developed React + TypeScript web application with Vite
- Integrated Leaflet.js for interactive map visualization
- Created responsive design with Tailwind CSS
- Implemented facility list with detainee counts

### Phase 4: Mobile App Implementation ✅
- Integrated heatmap view into React Native mobile app
- Added tab navigation between search and heatmap views
- Created map visualization using react-native-maps
- Implemented facility list with color-coded detainee counts

### Phase 5: Deployment 🚧
- Preparing deployment configurations
- Creating production deployment scripts
- Setting up monitoring and logging

## Key Features

### Database Schema
- **Detainee**: Personal information and identifiers
- **Facility**: Location information with GPS coordinates
- **DetaineeLocationHistory**: Timestamped location tracking

### API Endpoints
- `GET /api/facilities` - List all facilities
- `GET /api/facility/{id}/current-detainees` - Facility details
- `GET /api/heatmap-data` - Aggregated heatmap data

### Web Application
- Interactive map with zoom and pan
- Color-coded markers based on detainee density
- Facility information popups
- Responsive design for all devices

### Mobile Application
- Tab-based navigation between search and heatmap
- Interactive map with facility markers
- Facility list with current detainee counts
- Caching for improved performance

## Technology Stack

### Backend
- Python 3.9+
- FastAPI
- PostgreSQL
- Psycopg2

### Frontend
- React (Web)
- React Native (Mobile)
- TypeScript
- Leaflet.js / react-leaflet
- react-native-maps
- Tailwind CSS

### Development Tools
- Vite (Web app build tool)
- Expo (Mobile development platform)
- Git (Version control)

## Directory Structure
```
├── src/
│   └── ice_locator_mcp/
│       ├── api/          # Heatmap API implementation
│       ├── database/     # Database models and manager
│       └── core/         # Core application logic
├── tests/                # Unit and integration tests
├── web-app/              # React web application
├── mobile-app/           # React Native mobile application
├── docs/                 # Project documentation
└── scripts/              # Utility scripts
```

## Getting Started

### Prerequisites
- Python 3.9+
- Node.js 14+
- PostgreSQL 12+
- Git

### Installation
1. Clone the repository
2. Set up Python virtual environment
3. Install Python dependencies
4. Install Node.js dependencies for web and mobile apps
5. Set up PostgreSQL database
6. Run database seeding scripts

### Running the Applications
1. Start the heatmap API server
2. Start the web application (Vite dev server)
3. Start the mobile application (Expo dev server)

## Testing
- Unit tests for database operations
- API endpoint tests
- Component tests for web and mobile interfaces
- Integration tests for end-to-end functionality

## Documentation
- Detailed implementation summaries for each phase
- API documentation
- Deployment guides
- User manuals

## Contributing
This project follows standard Git flow practices:
1. Create feature branches from `develop`
2. Submit pull requests for code review
3. Merge to `develop` after approval
4. Release to `main` for production deployments

## License
This project is proprietary and confidential.

## Contact
For questions about this implementation, please contact the development team.
