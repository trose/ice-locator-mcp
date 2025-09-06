# How to Look Up a Detainee's Name Using ICE Locator MCP

## For AI Agents: Direct MCP Tool Usage

As an AI agent, you can directly call the ICE Locator MCP tools without writing additional scripts. The MCP server exposes several tools that you can invoke directly through the Model Context Protocol.

## Available MCP Tools

### 1. `search_detainee_by_name`
Search for a detainee using their personal information.

**Parameters:**
- `first_name` (string, required): Detainee's first name
- `last_name` (string, required): Detainee's last name
- `date_of_birth` (string, required): Date of birth in YYYY-MM-DD format
- `country_of_birth` (string, required): Country of birth
- `middle_name` (string, optional): Middle name
- `language` (string, optional): Response language (default: en)
- `fuzzy_search` (boolean, optional): Enable fuzzy name matching (default: true)

**Example Usage:**
```
{
  "name": "search_detainee_by_name",
  "arguments": {
    "first_name": "JOSE",
    "last_name": "GARCIA",
    "date_of_birth": "1980-01-01",
    "country_of_birth": "Mexico"
  }
}
```

### 2. `search_detainee_by_alien_number`
Search for a detainee using their alien registration number.

**Parameters:**
- `alien_number` (string, required): Alien registration number (A followed by 8-9 digits)
- `language` (string, optional): Response language (default: en)

**Example Usage:**
```
{
  "name": "search_detainee_by_alien_number",
  "arguments": {
    "alien_number": "A123456789"
  }
}
```

### 3. `smart_detainee_search`
Perform an AI-powered search using natural language queries.

**Parameters:**
- `query` (string, required): Natural language search query
- `context` (string, optional): Additional context for the search
- `suggest_corrections` (boolean, optional): Enable auto-correction suggestions (default: true)
- `language` (string, optional): Response language (default: en)

**Example Usage:**
```
{
  "name": "smart_detainee_search",
  "arguments": {
    "query": "Find Jose Garcia from Mexico born in 1980"
  }
}
```

### 4. `bulk_search_detainees`
Search for multiple detainees simultaneously.

**Parameters:**
- `search_requests` (array, required): List of search requests
- `max_concurrent` (integer, optional): Maximum concurrent searches (default: 3, max: 5)
- `continue_on_error` (boolean, optional): Continue processing if some searches fail (default: true)

**Example Usage:**
```
{
  "name": "bulk_search_detainees",
  "arguments": {
    "search_requests": [
      {
        "first_name": "JOSE",
        "last_name": "GARCIA",
        "date_of_birth": "1980-01-01",
        "country_of_birth": "Mexico"
      },
      {
        "first_name": "MARIA",
        "last_name": "RODRIGUEZ",
        "date_of_birth": "1985-05-15",
        "country_of_birth": "Guatemala"
      }
    ]
  }
}
```

### 5. `generate_search_report`
Generate comprehensive reports for legal or advocacy use.

**Parameters:**
- `search_criteria` (object, required): Original search parameters
- `results` (array, required): Search results to include in report
- `report_type` (string, optional): Type of report (legal, advocacy, family)
- `format` (string, optional): Output format (markdown, json)

## Processing Search Results

When you receive results from any search tool, the response will include:

1. **Status**: "found", "not_found", or "error"
2. **Results**: Array of detainee records (if found)
3. **Metadata**: Additional information about the search

### Sample Successful Response:
```json
{
  "status": "found",
  "results": [
    {
      "name": "JOSE GARCIA",
      "alien_number": "A123456789",
      "date_of_birth": "1980-01-01",
      "country_of_birth": "Mexico",
      "facility_name": "Alligator Alcatraz Detention Center",
      "facility_location": "Everglades, FL",
      "custody_status": "In Detention",
      "last_updated": "2025-08-28T15:30:45Z"
    }
  ]
}
```

### Sample Not Found Response:
```json
{
  "status": "not_found",
  "message": "No detainees found matching the provided criteria"
}
```

## Important Notes for AI Agents

1. **Use Proper Tool Names**: Always use the exact tool names as listed above
2. **Handle All Response Types**: Be prepared to process "found", "not_found", and "error" responses
3. **Respect Rate Limits**: The system implements rate limiting; avoid making too many requests too quickly
4. **Enable Fuzzy Search**: For name searches, consider enabling fuzzy matching to catch variations
5. **Process Results Structured**: Extract location, status, and updated_at information from successful responses
6. **No Direct API Calls**: Do not attempt to call the ICE website directly; always use the MCP tools to avoid 403 errors

## Extracting Required Information

From successful search results, extract these key fields for your CSV:
- `name`: Full name of detainee
- `alien_number`: Alien registration number
- `date_of_birth`: Date of birth
- `country_of_birth`: Country of birth
- `facility_name`: Detention facility name
- `facility_location`: Facility location
- `custody_status`: Current custody status
- `last_updated`: When record was last updated