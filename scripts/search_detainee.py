#!/usr/bin/env python3
"""
Simple script to search for a specific detainee using the ICE Locator MCP Server.

Usage:
    python search_detainee.py <first_name> <last_name> [date_of_birth] [country_of_birth]
    python search_detainee.py --alien-number <alien_number>
"""

import asyncio
import csv
import json
import sys
import os
from typing import Dict, Optional

# Add the src directory to the path so we can import the MCP server
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ice_locator_mcp.core.search_engine import SearchEngine, SearchRequest
from ice_locator_mcp.core.config import SearchConfig, ProxyConfig as ConfigProxyConfig
from ice_locator_mcp.anti_detection.proxy_manager import ProxyManager

async def search_detainee_by_name(first_name: str, last_name: str, 
                                date_of_birth: str = "", country_of_birth: str = "") -> Dict:
    """
    Search for a detainee by name using the MCP server.
    
    Args:
        first_name: Detainee's first name
        last_name: Detainee's last name
        date_of_birth: Date of birth (YYYY-MM-DD format)
        country_of_birth: Country of birth
        
    Returns:
        Dictionary with search results
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
                "results": [],
                "error_message": result.search_metadata.get("error_message", "No results found")
            }
            
    finally:
        # Cleanup
        await search_engine.cleanup()
        await proxy_manager.cleanup()

async def search_detainee_by_alien_number(alien_number: str) -> Dict:
    """
    Search for a detainee by alien number using the MCP server.
    
    Args:
        alien_number: Alien registration number (A followed by 8-9 digits)
        
    Returns:
        Dictionary with search results
    """
    # Validate alien number format
    if not alien_number.startswith('A') or not (9 <= len(alien_number) <= 10):
        return {
            "status": "error",
            "error_message": "Invalid alien number format. Should be A followed by 8-9 digits."
        }
    
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
            alien_number=alien_number
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
                "results": [],
                "error_message": result.search_metadata.get("error_message", "No results found")
            }
            
    finally:
        # Cleanup
        await search_engine.cleanup()
        await proxy_manager.cleanup()

def find_detainee_in_csv(first_name: str, last_name: str, csv_file: str = "enriched_detainees.csv") -> Optional[Dict]:
    """
    Find a detainee in the CSV file.
    
    Args:
        first_name: Detainee's first name
        last_name: Detainee's last name
        csv_file: Path to the CSV file
        
    Returns:
        Dictionary with detainee information or None if not found
    """
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if (row['first_name'].upper() == first_name.upper() and 
                    row['last_name'].upper() == last_name.upper()):
                    return row
    except FileNotFoundError:
        print(f"CSV file {csv_file} not found")
        return None
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return None
    
    return None

async def main():
    """Main function to handle command line arguments and perform search."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python search_detainee.py <first_name> <last_name> [date_of_birth] [country_of_birth]")
        print("  python search_detainee.py --alien-number <alien_number>")
        print("  python search_detainee.py --csv <first_name> <last_name>")
        sys.exit(1)
    
    # Check if searching by alien number
    if sys.argv[1] == "--alien-number":
        if len(sys.argv) != 3:
            print("Usage: python search_detainee.py --alien-number <alien_number>")
            sys.exit(1)
        
        alien_number = sys.argv[2]
        print(f"Searching for detainee with alien number: {alien_number}")
        result = await search_detainee_by_alien_number(alien_number)
        
    # Check if searching in CSV
    elif sys.argv[1] == "--csv":
        if len(sys.argv) < 4:
            print("Usage: python search_detainee.py --csv <first_name> <last_name>")
            sys.exit(1)
        
        first_name = sys.argv[2]
        last_name = sys.argv[3]
        print(f"Searching for {first_name} {last_name} in CSV file...")
        result = find_detainee_in_csv(first_name, last_name)
        
        if result:
            print("Found in CSV:")
            print(json.dumps(result, indent=2))
        else:
            print("Not found in CSV")
        return
    
    # Search by name
    else:
        if len(sys.argv) < 3:
            print("Usage: python search_detainee.py <first_name> <last_name> [date_of_birth] [country_of_birth]")
            sys.exit(1)
        
        first_name = sys.argv[1]
        last_name = sys.argv[2]
        date_of_birth = sys.argv[3] if len(sys.argv) > 3 else ""
        country_of_birth = sys.argv[4] if len(sys.argv) > 4 else ""
        
        print(f"Searching for detainee: {first_name} {last_name}")
        if date_of_birth:
            print(f"Date of birth: {date_of_birth}")
        if country_of_birth:
            print(f"Country of birth: {country_of_birth}")
        
        result = await search_detainee_by_name(first_name, last_name, date_of_birth, country_of_birth)
    
    # Display results
    print("\nSearch Results:")
    print("=" * 50)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(main())