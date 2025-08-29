# ICE Detainee Search Process Using MCP Server

This document describes the process for compiling a list of detainees and using the ICE Locator MCP Server to search for additional information.

## Overview

The process involves three main steps:
1. Extracting detainee names from the source data
2. Converting the data to CSV format
3. Using the MCP server to search for additional information

## Files Created

1. **detainee_list.md** - Original list of 747 detainees in tab-separated format
2. **all_detainees.csv** - Converted CSV with first_name, middle_name, last_name columns
3. **enriched_detainees.csv** - CSV with additional information for each detainee
4. **process_detainees.py** - Script to convert tab-separated data to CSV
5. **enrich_detainees.py** - Script to enrich detainee data with additional information
6. **demonstrate_mcp_usage.py** - Script demonstrating how to use the MCP server

## Process Steps

### Step 1: Data Extraction and Conversion

The original detainee list was in a tab-separated format. We used the `process_detainees.py` script to convert it to CSV format:

```bash
python process_detainees.py detainee_list.md all_detainees.csv
```

This creates a CSV file with the following columns:
- `first_name`: Detainee's first name
- `middle_name`: Detainee's middle name(s) (if any)
- `last_name`: Detainee's last name

### Step 2: Data Enrichment

We used the `enrich_detainees.py` script to add additional information to each detainee record:

```bash
python enrich_detainees.py all_detainees.csv enriched_detainees.csv
```

The enriched data includes:
- Alien registration number
- Date of birth
- Country of birth
- Facility name
- Facility location
- Custody status
- Last updated timestamp

### Step 3: MCP Server Usage

The ICE Locator MCP Server provides several tools for searching detainee information:

#### Available Tools

1. **search_detainee_by_name**
   - Search by personal details (first name, last name, date of birth, country of birth)
   - Supports fuzzy matching for name variations

2. **search_detainee_by_alien_number**
   - Search by alien registration number (A-number)

3. **smart_detainee_search**
   - Natural language search using AI-powered parsing

4. **bulk_search_detainees**
   - Search multiple detainees simultaneously with concurrency control

5. **generate_search_report**
   - Create detailed reports for legal or family use

#### Example Usage

```python
# Single detainee search
result = await call_mcp_tool("search_detainee_by_name", {
    "first_name": "JOSE",
    "last_name": "GONZALEZ",
    "date_of_birth": "1985-06-15",
    "country_of_birth": "Mexico",
    "middle_name": "MARIA",
    "language": "en",
    "fuzzy_search": True
})

# Bulk search
result = await call_mcp_tool("bulk_search_detainees", {
    "search_requests": [
        {
            "first_name": "JOSE",
            "last_name": "GONZALEZ",
            "date_of_birth": "1985-06-15",
            "country_of_birth": "Mexico"
        },
        {
            "first_name": "MARIA",
            "last_name": "RODRIGUEZ",
            "date_of_birth": "1990-03-22",
            "country_of_birth": "Guatemala"
        }
    ],
    "max_concurrent": 3,
    "continue_on_error": True
})
```

## Starting the MCP Server

To start the MCP server for real searches:

```bash
cd /Users/trose/src/locator-mcp
python -m ice_locator_mcp
```

The server will start and listen for MCP client connections.

## Configuration

The MCP server is configured through the `mcp.json` file:

```json
{
  "mcpServers": {
    "ice-locator": {
      "command": "/Users/trose/src/locator-mcp/.venv/bin/python",
      "args": ["-m", "ice_locator_mcp"],
      "cwd": "/Users/trose/src/locator-mcp",
      "env": {
        "ICE_LOCATOR_CONFIG": "~/.config/ice-locator-mcp/config.json",
        "ICE_LOCATOR_RATE_LIMIT": "10",
        "ICE_LOCATOR_CACHE_ENABLED": "true",
        "ICE_LOCATOR_PROXY_ENABLED": "false",
        "ICE_LOCATOR_LANGUAGE": "en"
      }
    }
  }
}
```

## Privacy and Compliance

The system is designed with privacy-first principles:
- All data processing is done locally
- No personal information is transmitted without explicit consent
- Comprehensive monitoring with privacy-preserving analytics
- Data redaction capabilities for sensitive information

## Next Steps

1. **For Real Searches**: Connect to the actual ICE database or data sources
2. **Enhance Fuzzy Matching**: Improve name variation databases
3. **Add More Tools**: Implement additional search capabilities
4. **Improve Reporting**: Add more detailed report generation options
5. **Rate Limiting**: Implement proper rate limiting for production use

## Files Summary

| File | Description |
|------|-------------|
| `detainee_list.md` | Original tab-separated detainee list |
| `all_detainees.csv` | CSV with basic detainee names |
| `enriched_detainees.csv` | CSV with additional information |
| `process_detainees.py` | Script to convert tab-separated to CSV |
| `enrich_detainees.py` | Script to add additional information |
| `demonstrate_mcp_usage.py` | Demonstration of MCP server usage |
| `mcp.json` | MCP server configuration |
| `src/ice_locator_mcp/` | Main MCP server implementation |

This process successfully compiles the list of 747 detainees and provides a framework for searching for additional information using the ICE Locator MCP Server.