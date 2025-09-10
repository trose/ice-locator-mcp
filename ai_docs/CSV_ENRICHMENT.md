# CSV Enrichment with ICE Locator MCP Server

This document explains how to use the MCP server to enrich the [sample_detainees.csv](file:///Users/trose/src/locator-mcp/sample_detainees.csv) file with additional data about detainees.

## Available Scripts

### 1. `enrich_csv_with_mcp.py`

This script connects to the ICE Locator MCP Server and uses it to search for additional information about each detainee in the [sample_detainees.csv](file:///Users/trose/src/locator-mcp/sample_detainees.csv) file.

**Usage:**
```bash
python enrich_csv_with_mcp.py
```

**How it works:**
1. Reads the [sample_detainees.csv](file:///Users/trose/src/locator-mcp/sample_detainees.csv) file
2. For each detainee, calls the MCP server's `search_detainee_by_name` tool
3. Gathers additional information such as:
   - Alien registration number
   - Date of birth
   - Country of birth
   - Facility name and location
   - Custody status
   - Last updated timestamp
4. Saves the enriched data to a new CSV file

**Note:** This script requires the MCP server to be properly configured with real data sources. In the current implementation, it uses simulated responses.

### 2. `enrich_csv_demo.py`

This script demonstrates how the enrichment process would work with realistic data without requiring the MCP server.

**Usage:**
```bash
python enrich_csv_demo.py
```

**How it works:**
1. Reads the [sample_detainees.csv](file:///Users/trose/src/locator-mcp/sample_detainees.csv) file
2. Uses the [enriched_detainees.csv](file:///Users/trose/src/locator-mcp/enriched_detainees.csv) file as a reference for realistic data
3. For each detainee, generates realistic mock data based on patterns in the reference data
4. Saves the demo enriched data to `demo_enriched_detainees.csv`

## File Formats

### Input: sample_detainees.csv
```csv
first_name,middle_name,last_name
ABDULLAH,,ALHAMZAH
ABDULMAJED,,ABDULMANE
ABEL,HERNANDEZ,PEREZ
...
```

### Output: [enriched format]
```csv
first_name,middle_name,last_name,alien_number,date_of_birth,country_of_birth,facility_name,facility_location,custody_status,last_updated
EXAMPLE,,NAME,A000000000,2000-01-25,Country,Facility Name,"City, State",Status,2025-08-28 23:32:49
...
```

## Running the Scripts

1. Make sure you're in the project directory:
   ```bash
   cd /Users/trose/src/locator-mcp
   ```

2. Run the demo script to see how enrichment would work:
   ```bash
   python enrich_csv_demo.py
   ```

3. (Optional) Run the actual MCP script:
   ```bash
   python enrich_csv_with_mcp.py
   ```

## Output Files

- `demo_enriched_detainees.csv` - Demo enriched data with realistic mock information
- `mcp_enriched_detainees_YYYYMMDD_HHMMSS.csv` - Actual enriched data from MCP server (if available)

## How the MCP Server Enrichment Works

The ICE Locator MCP Server provides several tools for searching detainee information:

1. **search_detainee_by_name** - Search by personal details
2. **search_detainee_by_alien_number** - Search by alien registration number
3. **smart_detainee_search** - Natural language search
4. **bulk_search_detainees** - Search multiple detainees simultaneously
5. **generate_search_report** - Create detailed reports for legal/family use

The enrichment script uses the `search_detainee_by_name` tool to gather additional information about each detainee.