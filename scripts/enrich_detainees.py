#!/usr/bin/env python3
"""
Enrich detainee data with additional information using the ICE Locator MCP Server.

This script reads the detainee CSV file and uses the MCP server to search for
additional information about each detainee.
"""

import asyncio
import csv
import json
import random
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import subprocess
import time
import os

# Add the src directory to the path so we can import the MCP server
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ice_locator_mcp.core.search_engine import SearchEngine, SearchRequest
from ice_locator_mcp.core.config import SearchConfig, ProxyConfig as ConfigProxyConfig
from ice_locator_mcp.anti_detection.proxy_manager import ProxyManager

# Sample facilities for demonstration
FACILITIES = [
    "Alligator Alcatraz Detention Center",
    "Miami Processing Center",
    "Broward Transitional Center",
    "Florida State Prison",
    "Orange County Jail",
    "Palm Beach County Jail"
]

# Sample countries for demonstration
COUNTRIES = [
    "Mexico", "Guatemala", "El Salvador", "Honduras", "Nicaragua",
    "Costa Rica", "Panama", "Colombia", "Venezuela", "Ecuador",
    "Peru", "Bolivia", "Brazil", "Argentina", "Chile"
]

# Sample custody statuses
CUSTODY_STATUSES = [
    "In Detention", "Processing", "Awaiting Hearing", 
    "Awaiting Deportation", "Released on Bond"
]

def read_detainees_csv(filename: str) -> List[Dict[str, str]]:
    """Read detainees from CSV file."""
    detainees = []
    with open(filename, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            detainees.append(row)
    return detainees

def write_enriched_csv(detainees: List[Dict[str, str]], filename: str):
    """Write enriched detainee data to CSV file."""
    if not detainees:
        return
    
    fieldnames = list(detainees[0].keys())
    
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(detainees)

async def search_detainee_mcp(first_name: str, last_name: str, date_of_birth: str, 
                            country_of_birth: str, middle_name: str = "") -> Optional[Dict]:
    """
    Search for detainee using the ICE Locator MCP Server.
    
    This function calls the MCP server tools to get actual data.
    """
    # Create search configuration
    config = SearchConfig(
        base_url="https://locator.ice.gov",
        timeout=30,
        requests_per_minute=10,
        burst_allowance=5
    )
    
    # Create proxy configuration
    proxy_config = ConfigProxyConfig(
        enabled=True,
        rotation_interval=300,
        max_requests_per_proxy=10
    )
    
    # Initialize proxy manager
    proxy_manager = ProxyManager(proxy_config)
    await proxy_manager.initialize()
    
    try:
        # Initialize search engine
        search_engine = SearchEngine(proxy_manager, config)
        await search_engine.initialize()
        
        # Create search request
        search_request = SearchRequest(
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            date_of_birth=date_of_birth,
            country_of_birth=country_of_birth
        )
        
        # Perform search
        result = await search_engine.search(search_request)
        
        # Convert SearchResult to dictionary format
        if result.status == "found" and result.results:
            detainee_result = result.results[0]
            return {
                "status": result.status,
                "results": [{
                    "name": detainee_result.name,
                    "alien_number": detainee_result.alien_number,
                    "date_of_birth": detainee_result.date_of_birth,
                    "country_of_birth": detainee_result.country_of_birth,
                    "facility_name": detainee_result.facility_name,
                    "facility_location": detainee_result.facility_location,
                    "custody_status": detainee_result.custody_status,
                    "last_updated": detainee_result.last_updated
                }]
            }
        else:
            return {
                "status": result.status,
                "results": []
            }
            
    finally:
        # Cleanup
        await search_engine.cleanup()
        await proxy_manager.cleanup()

async def enrich_all_detainees(input_file: str, output_file: str, use_mcp: bool = False):
    """
    Enrich all detainees with additional information.
    """
    print(f"Reading detainees from {input_file}")
    detainees = read_detainees_csv(input_file)
    print(f"Found {len(detainees)} detainees")
    
    enriched_detainees = []
    
    for i, detainee in enumerate(detainees, 1):
        if i % 50 == 0:
            print(f"Processed {i}/{len(detainees)} detainees")
        
        try:
            if use_mcp:
                # Call the MCP server for real data
                result = await search_detainee_mcp(
                    detainee["first_name"],
                    detainee["last_name"],
                    "",  # date_of_birth not in original data
                    "",  # country_of_birth not in original data
                    detainee["middle_name"]
                )
                
                if result and result.get("status") == "found":
                    enriched_data = result["results"][0]
                    # Add original names to the enriched data
                    enriched_data["first_name"] = detainee["first_name"]
                    enriched_data["middle_name"] = detainee["middle_name"]
                    enriched_data["last_name"] = detainee["last_name"]
                else:
                    print(f"No data found for {detainee['first_name']} {detainee['last_name']}")
                    # Skip this detainee if no data found
                    continue
            else:
                print("MCP integration is required for real data. Please use --use-mcp flag.")
                return
            
            enriched_detainees.append(enriched_data)
            
        except Exception as e:
            print(f"Error processing detainee {i}: {detainee}")
            print(f"Error: {e}")
            # Skip this detainee on error
            continue
    
    print(f"Writing enriched data to {output_file}")
    write_enriched_csv(enriched_detainees, output_file)
    print(f"Successfully enriched {len(enriched_detainees)} detainees")

def main():
    if len(sys.argv) < 3:
        print("Usage: python enrich_detainees.py <input_file> <output_file> [--use-mcp]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    use_mcp = "--use-mcp" in sys.argv
    
    if not use_mcp:
        print("Error: Real data integration requires --use-mcp flag.")
        print("Usage: python enrich_detainees.py <input_file> <output_file> --use-mcp")
        sys.exit(1)
    
    print(f"Enriching detainees from {input_file}")
    print(f"Output file: {output_file}")
    print(f"Using MCP server: {use_mcp}")
    
    # Run the async function
    asyncio.run(enrich_all_detainees(input_file, output_file, use_mcp))

if __name__ == "__main__":
    main()