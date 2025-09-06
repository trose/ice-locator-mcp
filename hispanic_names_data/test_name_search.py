#!/usr/bin/env python3
"""
Simple test script to verify name search functionality with a few sample names.
"""

import asyncio
import csv
import os
import sys
from datetime import datetime

# Add the src directory to the path so we can import the MCP server
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ice_locator_mcp.core.search_engine import SearchEngine, SearchRequest
from ice_locator_mcp.core.config import SearchConfig, ProxyConfig as ConfigProxyConfig
from ice_locator_mcp.anti_detection.proxy_manager import ProxyManager

async def search_single_name(first_name: str, last_name: str) -> dict:
    """Search for a single name and return the result."""
    try:
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
                date_of_birth="1980-01-01",
                country_of_birth="Mexico"
            )
            
            # Perform search
            result = await search_engine.search(search_request)
            
            # Process results
            if result.status == "found" and result.results:
                detainee_result = result.results[0]
                return {
                    "status": "found",
                    "full_name": f"{first_name} {last_name}",
                    "first_name": first_name,
                    "last_name": last_name,
                    "alien_number": detainee_result.alien_number,
                    "date_of_birth": detainee_result.date_of_birth,
                    "country_of_birth": detainee_result.country_of_birth,
                    "facility_name": detainee_result.facility_name,
                    "facility_location": detainee_result.facility_location,
                    "custody_status": detainee_result.custody_status,
                    "last_updated": detainee_result.last_updated,
                    "search_timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "not_found",
                    "full_name": f"{first_name} {last_name}",
                    "first_name": first_name,
                    "last_name": last_name
                }
                
        finally:
            # Cleanup
            await search_engine.cleanup()
            await proxy_manager.cleanup()
            
    except Exception as e:
        return {
            "status": "error",
            "full_name": f"{first_name} {last_name}",
            "error": str(e)
        }

def read_test_names(filename: str) -> list:
    """Read test names from file."""
    names = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split()
                    if len(parts) >= 2:
                        first_name = parts[0]
                        last_name = " ".join(parts[1:])
                        names.append((first_name, last_name))
    except Exception as e:
        print(f"Error reading test names: {e}")
    return names

def save_results_to_csv(results: list, filename: str = "test_search_results.csv"):
    """Save results to CSV file."""
    if not results:
        return
        
    # Define CSV headers
    headers = [
        "status", "full_name", "first_name", "last_name", "alien_number",
        "date_of_birth", "country_of_birth", "facility_name",
        "facility_location", "custody_status", "last_updated", "search_timestamp", "error"
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        
        for result in results:
            # Ensure all headers are present in each row
            row = {header: result.get(header, "") for header in headers}
            writer.writerow(row)
    
    print(f"Results saved to {filename}")

async def main():
    """Main function to run the test."""
    print("Starting test name search...")
    
    # Read test names
    test_names_file = "test_names.txt"
    names = read_test_names(test_names_file)
    
    if not names:
        print("No test names found. Creating sample names...")
        # Use some common Hispanic names for testing
        names = [
            ("JOSE", "GARCIA"),
            ("MARIA", "RODRIGUEZ"),
            ("CARLOS", "MARTINEZ"),
            ("ANA", "LOPEZ"),
            ("MIGUEL", "GONZALEZ")
        ]
    
    print(f"Testing {len(names)} names:")
    for first, last in names:
        print(f"  - {first} {last}")
    
    # Search for each name
    results = []
    for i, (first_name, last_name) in enumerate(names):
        print(f"\nSearching {i+1}/{len(names)}: {first_name} {last_name}")
        result = await search_single_name(first_name, last_name)
        results.append(result)
        
        # Print result
        if result["status"] == "found":
            print(f"  FOUND: {result['facility_name']} - {result['custody_status']}")
        elif result["status"] == "not_found":
            print(f"  NOT FOUND")
        else:
            print(f"  ERROR: {result.get('error', 'Unknown error')}")
    
    # Save results
    save_results_to_csv(results, "test_search_results.csv")
    
    # Print summary
    found_count = sum(1 for r in results if r["status"] == "found")
    not_found_count = sum(1 for r in results if r["status"] == "not_found")
    error_count = sum(1 for r in results if r["status"] == "error")
    
    print(f"\nSearch Summary:")
    print(f"  Total names searched: {len(results)}")
    print(f"  Found: {found_count}")
    print(f"  Not found: {not_found_count}")
    print(f"  Errors: {error_count}")

if __name__ == "__main__":
    asyncio.run(main())