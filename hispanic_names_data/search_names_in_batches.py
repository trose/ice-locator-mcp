#!/usr/bin/env python3
"""
Script to search for Hispanic/Latino names in the ICE Locator database
and generate a CSV with results that include location and status information.
"""

import asyncio
import csv
import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional

# Add the src directory to the path so we can import the MCP server
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ice_locator_mcp.core.search_engine import SearchEngine, SearchRequest
from ice_locator_mcp.core.config import SearchConfig, ProxyConfig as ConfigProxyConfig
from ice_locator_mcp.anti_detection.proxy_manager import ProxyManager

# Default values for search parameters
DEFAULT_COUNTRY = "Mexico"  # Most common Hispanic country of origin
DEFAULT_DOB = "1980-01-01"  # Generic date of birth if not specified

class NameSearcher:
    """Class to handle searching for names in the ICE database."""
    
    def __init__(self, output_csv: str = "detainee_search_results.csv"):
        """Initialize the name searcher."""
        self.output_csv = output_csv
        self.results_count = 0
        self.processed_count = 0
        self.found_count = 0
        
        # Create or initialize the CSV file with headers
        self._initialize_csv()
        
    def _initialize_csv(self):
        """Initialize the CSV file with headers."""
        headers = [
            "full_name", "first_name", "last_name", "alien_number", 
            "date_of_birth", "country_of_birth", "facility_name", 
            "facility_location", "custody_status", "last_updated", "search_timestamp"
        ]
        
        # Check if file exists and has content
        file_exists = os.path.exists(self.output_csv) and os.path.getsize(self.output_csv) > 0
        
        if not file_exists:
            with open(self.output_csv, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
            print(f"Initialized CSV file: {self.output_csv}")
        
    async def search_name(self, full_name: str) -> Optional[Dict]:
        """
        Search for a detainee by full name.
        
        Args:
            full_name: Full name in format "FirstName LastName"
            
        Returns:
            Dictionary with search results or None if no results
        """
        # Parse the full name
        parts = full_name.strip().split()
        if len(parts) < 2:
            print(f"Skipping invalid name: {full_name}")
            return None
            
        first_name = parts[0]
        last_name = " ".join(parts[1:])  # Handle compound last names
        
        try:
            # Create search configuration
            config = SearchConfig(
                base_url="https://locator.ice.gov",
                timeout=30,
                requests_per_minute=10,  # Conservative rate limiting
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
                    date_of_birth=DEFAULT_DOB,
                    country_of_birth=DEFAULT_COUNTRY
                )
                
                # Perform search
                result = await search_engine.search(search_request)
                
                # Process results
                if result.status == "found" and result.results:
                    detainee_result = result.results[0]
                    return {
                        "full_name": full_name,
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
                    return None
                    
            finally:
                # Cleanup
                await search_engine.cleanup()
                await proxy_manager.cleanup()
                
        except Exception as e:
            print(f"Error searching for {full_name}: {str(e)}")
            return None
    
    def save_result(self, result: Dict):
        """Save a single result to the CSV file."""
        if result:
            row = [
                result["full_name"],
                result["first_name"],
                result["last_name"],
                result["alien_number"],
                result["date_of_birth"],
                result["country_of_birth"],
                result["facility_name"],
                result["facility_location"],
                result["custody_status"],
                result["last_updated"],
                result["search_timestamp"]
            ]
            
            with open(self.output_csv, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(row)
            
            self.found_count += 1
            print(f"Found result for: {result['full_name']} - {result['custody_status']} at {result['facility_name']}")
    
    def read_names_from_file(self, filename: str) -> List[str]:
        """Read names from the file, skipping comment lines."""
        names = []
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comment lines
                    if line and not line.startswith('#'):
                        names.append(line)
        except FileNotFoundError:
            print(f"Error: File {filename} not found.")
        except Exception as e:
            print(f"Error reading file {filename}: {str(e)}")
        
        return names
    
    async def search_names_batch(self, names: List[str], batch_size: int = 5, delay: float = 2.0):
        """
        Search for names in batches to avoid overwhelming the system.
        
        Args:
            names: List of names to search for
            batch_size: Number of concurrent searches
            delay: Delay between batches in seconds
        """
        print(f"Processing {len(names)} names in batches of {batch_size}")
        
        for i in range(0, len(names), batch_size):
            batch = names[i:i + batch_size]
            print(f"\nProcessing batch {i//batch_size + 1}/{(len(names)-1)//batch_size + 1}")
            
            # Process batch concurrently
            tasks = [self.search_name(name) for name in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Save results
            for result in results:
                if isinstance(result, dict):
                    self.save_result(result)
                elif isinstance(result, Exception):
                    print(f"Error in search: {str(result)}")
            
            self.processed_count += len(batch)
            print(f"Processed: {self.processed_count}/{len(names)} names, Found: {self.found_count} matches")
            
            # Delay between batches unless it's the last batch
            if i + batch_size < len(names):
                print(f"Waiting {delay} seconds before next batch...")
                await asyncio.sleep(delay)
    
    async def run_search(self, input_file: str, max_names: Optional[int] = None):
        """
        Run the search process on names from the input file.
        
        Args:
            input_file: Path to the file containing names
            max_names: Maximum number of names to process (None for all)
        """
        print(f"Starting search process for names in {input_file}")
        print(f"Results will be saved to {self.output_csv}")
        
        # Read names from file
        names = self.read_names_from_file(input_file)
        
        if not names:
            print("No names found in the input file.")
            return
        
        print(f"Found {len(names)} names in the input file.")
        
        # Limit the number of names if specified
        if max_names:
            names = names[:max_names]
            print(f"Limited to processing first {len(names)} names.")
        
        # Process names in batches
        start_time = time.time()
        try:
            await self.search_names_batch(names, batch_size=3, delay=3.0)
        except KeyboardInterrupt:
            print("\nSearch interrupted by user.")
        except Exception as e:
            print(f"\nError during search: {str(e)}")
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\nSearch completed!")
        print(f"Total names processed: {self.processed_count}")
        print(f"Matches found: {self.found_count}")
        print(f"Time elapsed: {duration:.2f} seconds")
        print(f"Average time per name: {duration/self.processed_count:.2f} seconds" if self.processed_count > 0 else "")
        print(f"Results saved to: {self.output_csv}")

async def main():
    """Main function to run the name search process."""
    # Initialize the searcher
    searcher = NameSearcher("detainee_search_results.csv")
    
    # Input file path
    input_file = "organized/hispanic_full_names_extended_huge.txt"
    full_path = os.path.join(os.path.dirname(__file__), input_file)
    
    # Check if input file exists
    if not os.path.exists(full_path):
        print(f"Error: Input file {full_path} not found.")
        print("Please run the name generation script first.")
        return
    
    # Run the search - limit to first 1000 names for testing
    # You can increase this number or remove the limit for a full search
    await searcher.run_search(full_path, max_names=1000)

if __name__ == "__main__":
    asyncio.run(main())