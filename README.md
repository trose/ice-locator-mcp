# ICE Locator MCP Server

[![MCP Badge](https://lobehub.com/badge/mcp/trose-ice-locator-mcp)](https://lobehub.com/mcp/trose-ice-locator-mcp)

A Model Context Protocol (MCP) server for searching ICE detainee locations with AI-powered natural language queries.

## Features

- 🔍 **Smart Search**: Natural language queries with fuzzy matching
- 📊 **Bulk Operations**: Search multiple detainees simultaneously  
- 🌐 **Multilingual**: Support for English, Spanish, and more
- 📋 **Legal Reports**: Generate comprehensive reports for legal use
- 🗺️ **Heatmap Visualization**: Interactive web app showing facility locations

## Quick Start

### Installation

```bash
pip install ice-locator-mcp
```

### Claude Desktop Configuration

Add to your Claude Desktop config:

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

## Usage Examples

```python
# Natural language search
result = await smart_detainee_search(
    query="Find Maria Rodriguez from Guatemala born around 1985"
)

# Name-based search
result = await search_detainee_by_name(
    first_name="John",
    last_name="Doe", 
    date_of_birth="1990-01-15",
    country_of_birth="Mexico"
)

# Bulk search
result = await bulk_search_detainees(
    search_requests=[...],
    max_concurrent=3
)
```

## Web App

View the interactive heatmap: **[ice-locator-mcp.vercel.app](https://ice-locator-mcp.vercel.app/)**

## Use Cases

- **Legal Representatives**: Locate clients in ICE custody
- **Family Members**: Find detained relatives with AI assistance
- **Advocacy Organizations**: Streamline detainee location workflows
- **AI Assistants**: Enable immigration-related support capabilities

## Privacy & Security

- **No Data Storage**: Search data is not permanently stored
- **Local Processing**: All processing happens locally
- **Optional Analytics**: Privacy-first analytics with automatic data redaction
- **Rate Limiting**: Respectful usage with built-in rate limiting

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/trose/ice-locator-mcp/issues)
- **Documentation**: [Full Documentation](https://trose.github.io/ice-locator-mcp)

---

**⚠️ Important**: This is an independent project not affiliated with ICE. Use responsibly and in compliance with applicable laws.