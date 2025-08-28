# ICE Locator MCP Server API Documentation

## Overview

The ICE Locator MCP Server provides tools for searching ICE detention facilities and locating detainees through the Model Context Protocol (MCP). This documentation covers all available tools, their parameters, response formats, and usage examples.

## Authentication

The MCP server currently operates without authentication for public ICE data access. Rate limiting is applied to prevent abuse.

## Base Configuration

```json
{
  "mcpServers": {
    "ice-locator": {
      "command": "ice-locator-mcp",
      "args": [],
      "env": {
        "ICE_LOCATOR_CONFIG": "/path/to/config.json"
      }
    }
  }
}
```

## Available Tools

### 1. search_by_name

Search for detainees by name.

**Tool Name:** `search_by_name`

**Description:** Search ICE detainee database by first and last name with optional middle name.

#### Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `first_name` | string | Yes | First name of the person | "John" |
| `last_name` | string | Yes | Last name of the person | "Doe" |
| `middle_name` | string | No | Middle name or initial | "William" |
| `fuzzy_match` | boolean | No | Enable fuzzy matching for names | true |
| `confidence_threshold` | number | No | Minimum confidence score (0.0-1.0) | 0.8 |

#### Request Example

```json
{
  "method": "tools/call",
  "params": {
    "name": "search_by_name",
    "arguments": {
      "first_name": "John",
      "last_name": "Doe",
      "middle_name": "William",
      "fuzzy_match": true,
      "confidence_threshold": 0.8
    }
  }
}
```

#### Response Schema

```json
{
  "content": [
    {
      "type": "text",
      "text": "Search Results for John William Doe:\n\n..."
    }
  ],
  "isError": false
}
```

#### Response Data Structure

```json
{
  "results": [
    {
      "name": "John William Doe",
      "alien_number": "A123456789",
      "facility_name": "Example Detention Center",
      "facility_address": "123 Main St, City, ST 12345",
      "booking_date": "2023-01-15",
      "status": "In Custody",
      "confidence_score": 0.95,
      "match_details": {
        "name_similarity": 0.98,
        "phonetic_match": true,
        "fuzzy_components": {
          "first_name": 1.0,
          "last_name": 1.0,
          "middle_name": 0.9
        }
      }
    }
  ],
  "search_metadata": {
    "query_time": "2023-12-01T10:30:00Z",
    "total_results": 1,
    "search_type": "name_fuzzy",
    "processing_time_ms": 1250
  }
}
```

#### Error Responses

**Validation Error:**
```json
{
  "content": [
    {
      "type": "text", 
      "text": "Error: Invalid search parameters. First name and last name are required."
    }
  ],
  "isError": true
}
```

**Rate Limit Error:**
```json
{
  "content": [
    {
      "type": "text",
      "text": "Error: Rate limit exceeded. Please wait before making another request."
    }
  ],
  "isError": true
}
```

### 2. search_by_alien_number

Search for detainees by Alien Registration Number (A-Number).

**Tool Name:** `search_by_alien_number`

**Description:** Search ICE detainee database by Alien Registration Number.

#### Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `alien_number` | string | Yes | A-Number (with or without 'A' prefix) | "A123456789" or "123456789" |
| `validate_format` | boolean | No | Validate A-Number format | true |

#### Request Example

```json
{
  "method": "tools/call",
  "params": {
    "name": "search_by_alien_number", 
    "arguments": {
      "alien_number": "A123456789",
      "validate_format": true
    }
  }
}
```

#### Response Schema

```json
{
  "content": [
    {
      "type": "text",
      "text": "Search Results for A-Number A123456789:\n\n..."
    }
  ],
  "isError": false
}
```

#### Response Data Structure

```json
{
  "results": [
    {
      "name": "John William Doe",
      "alien_number": "A123456789", 
      "facility_name": "Example Detention Center",
      "facility_address": "123 Main St, City, ST 12345",
      "booking_date": "2023-01-15",
      "status": "In Custody",
      "last_updated": "2023-12-01T08:15:00Z"
    }
  ],
  "search_metadata": {
    "query_time": "2023-12-01T10:30:00Z",
    "total_results": 1,
    "search_type": "alien_number",
    "processing_time_ms": 850
  }
}
```

### 3. search_by_facility

Search for detainees by facility name or location.

**Tool Name:** `search_by_facility`

**Description:** Search for detainees at specific ICE detention facilities.

#### Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `facility_name` | string | No* | Name of the detention facility | "Example Detention Center" |
| `city` | string | No* | City where facility is located | "Houston" |
| `state` | string | No* | State where facility is located | "TX" |
| `zip_code` | string | No | ZIP code of facility | "77001" |

*At least one parameter is required

#### Request Example

```json
{
  "method": "tools/call",
  "params": {
    "name": "search_by_facility",
    "arguments": {
      "facility_name": "Example Detention Center",
      "city": "Houston",
      "state": "TX"
    }
  }
}
```

### 4. bulk_search

Perform bulk searches with multiple queries.

**Tool Name:** `bulk_search`

**Description:** Execute multiple search queries in a single request.

#### Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `searches` | array | Yes | Array of search query objects | See example below |
| `max_concurrent` | number | No | Maximum concurrent searches (1-5) | 3 |
| `include_summary` | boolean | No | Include summary statistics | true |

#### Request Example

```json
{
  "method": "tools/call",
  "params": {
    "name": "bulk_search",
    "arguments": {
      "searches": [
        {
          "type": "name",
          "first_name": "John",
          "last_name": "Doe"
        },
        {
          "type": "alien_number", 
          "alien_number": "A123456789"
        },
        {
          "type": "facility",
          "facility_name": "Example Center"
        }
      ],
      "max_concurrent": 3,
      "include_summary": true
    }
  }
}
```

### 5. get_facility_info

Get detailed information about detention facilities.

**Tool Name:** `get_facility_info`

**Description:** Retrieve detailed information about ICE detention facilities.

#### Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `facility_name` | string | No* | Exact facility name | "Example Detention Center" |
| `facility_id` | string | No* | Facility identifier | "FAC12345" |
| `include_capacity` | boolean | No | Include capacity information | true |
| `include_contact` | boolean | No | Include contact information | true |

*At least one identifier parameter is required

### 6. parse_natural_query

Parse natural language search queries.

**Tool Name:** `parse_natural_query`

**Description:** Parse natural language queries and convert them to structured search parameters.

#### Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `query` | string | Yes | Natural language search query | "Find John Doe at Houston facility" |
| `auto_execute` | boolean | No | Automatically execute parsed search | false |
| `confidence_threshold` | number | No | Minimum parsing confidence | 0.7 |

#### Request Example

```json
{
  "method": "tools/call",
  "params": {
    "name": "parse_natural_query",
    "arguments": {
      "query": "Find John Doe at Houston facility",
      "auto_execute": false,
      "confidence_threshold": 0.7
    }
  }
}
```

#### Response Data Structure

```json
{
  "parsed_query": {
    "search_type": "name_with_location",
    "parameters": {
      "first_name": "John",
      "last_name": "Doe", 
      "city": "Houston"
    },
    "confidence": 0.85,
    "alternatives": [
      {
        "search_type": "name",
        "parameters": {
          "first_name": "John",
          "last_name": "Doe"
        },
        "confidence": 0.95
      }
    ]
  },
  "suggestions": [
    "Did you mean to search for all John Does?",
    "Would you like to include fuzzy matching?"
  ]
}
```

## Error Codes

| Code | Type | Description | Resolution |
|------|------|-------------|------------|
| `INVALID_PARAMETERS` | Validation | Required parameters missing or invalid | Check parameter requirements |
| `RATE_LIMIT_EXCEEDED` | Rate Limiting | Too many requests in time window | Wait and retry |
| `SEARCH_TIMEOUT` | Timeout | Search operation timed out | Retry with more specific parameters |
| `FACILITY_NOT_FOUND` | Not Found | Specified facility doesn't exist | Verify facility name/location |
| `NO_RESULTS` | Empty Result | No matching records found | Try broader search criteria |
| `SERVICE_UNAVAILABLE` | Server Error | ICE service temporarily unavailable | Retry later |
| `CAPTCHA_REQUIRED` | Anti-bot | CAPTCHA challenge encountered | Automatic retry after delay |
| `BLOCKED_REQUEST` | Security | Request blocked by anti-detection | Automatic backoff and retry |

## Rate Limiting

The API implements adaptive rate limiting:

- **Default Limit:** 10 requests per minute
- **Burst Allowance:** 20 requests for initial burst
- **Adaptive Adjustment:** Rate automatically adjusts based on success/error rates

### Rate Limit Headers

Rate limit information is included in error responses:

```json
{
  "error": "Rate limit exceeded",
  "rate_limit": {
    "limit": 10,
    "remaining": 0,
    "reset_time": "2023-12-01T10:31:00Z",
    "retry_after": 60
  }
}
```

## Caching

The server implements intelligent caching:

- **Cache Duration:** 1 hour for search results
- **Cache Keys:** Based on search parameters (anonymized)
- **Cache Invalidation:** Automatic expiration and manual refresh

### Cache Control

Cache behavior can be controlled with parameters:

```json
{
  "cache_control": {
    "use_cache": true,
    "max_age": 3600,
    "force_refresh": false
  }
}
```

## Search Best Practices

### Name Searches

1. **Use fuzzy matching** for names with potential spelling variations
2. **Include middle name** when available for better accuracy
3. **Adjust confidence threshold** based on name commonality

```json
{
  "first_name": "José",
  "last_name": "García",
  "fuzzy_match": true,
  "confidence_threshold": 0.7
}
```

### A-Number Searches

1. **Include 'A' prefix** for validation
2. **Verify format** before submission
3. **Use exact match** for fastest results

```json
{
  "alien_number": "A123456789",
  "validate_format": true
}
```

### Facility Searches

1. **Use multiple identifiers** (name + location) for accuracy
2. **Check facility aliases** and alternate names
3. **Include state abbreviation** for disambiguation

## Integration Examples

### Python Client

```python
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def search_detainee():
    server_params = StdioServerParameters(
        command="ice-locator-mcp",
        args=[]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            result = await session.call_tool(
                "search_by_name",
                {
                    "first_name": "John",
                    "last_name": "Doe",
                    "fuzzy_match": True
                }
            )
            
            return result.content[0].text
```

### JavaScript Client

```javascript
import { Client } from '@modelcontextprotocol/client';
import { StdioTransport } from '@modelcontextprotocol/client/stdio';

async function searchDetainee() {
  const transport = new StdioTransport({
    command: 'ice-locator-mcp',
    args: []
  });
  
  const client = new Client(transport);
  await client.initialize();
  
  const result = await client.callTool('search_by_name', {
    first_name: 'John',
    last_name: 'Doe',
    fuzzy_match: true
  });
  
  return result.content[0].text;
}
```

### cURL Examples

**Search by Name:**
```bash
curl -X POST http://localhost:8000/mcp/call \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "search_by_name",
      "arguments": {
        "first_name": "John",
        "last_name": "Doe"
      }
    }
  }'
```

## Troubleshooting

### Common Issues

**No Results Found:**
- Verify spelling of names
- Try fuzzy matching
- Use partial names
- Check facility information

**Rate Limiting:**
- Reduce request frequency
- Implement exponential backoff
- Use bulk search for multiple queries

**Connection Issues:**
- Check server status
- Verify configuration
- Review proxy settings

**CAPTCHA Challenges:**
- Wait for automatic retry
- Reduce request rate
- Check IP reputation

### Debug Mode

Enable debug mode for detailed logging:

```json
{
  "debug": {
    "enabled": true,
    "log_level": "DEBUG",
    "include_timing": true,
    "log_requests": true
  }
}
```

## Support and Resources

- **GitHub Repository:** https://github.com/trose/ice-locator-mcp
- **Issue Tracker:** https://github.com/trose/ice-locator-mcp/issues
- **Documentation:** https://trose.github.io/ice-locator-mcp
- **MCP Protocol:** https://modelcontextprotocol.io

## Legal Notice

This tool provides access to publicly available information from ICE detention databases. Users are responsible for:

- Compliance with applicable laws and regulations
- Ethical use of personal information
- Respect for privacy and dignity of individuals
- Proper handling of sensitive information

The tool is designed for legitimate purposes including legal representation, family reunification, journalism, and advocacy work.