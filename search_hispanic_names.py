#!/usr/bin/env python3
"""
Script to search Hispanic/Latino names using ICE Locator MCP Server.
"""

import asyncio
import csv
import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add the src directory to the path so we can import the MCP components
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Sample date of birth and country of birth for our searches
SAMPLE_DOB = "1980-01-01"
SAMPLE_COUNTRIES = [
    "Mexico", "Guatemala", "El Salvador", "Honduras", "Nicaragua",
    "Costa Rica", "Panama", "Colombia", "Venezuela", "Ecuador",
    "Peru", "Bolivia", "Chile", "Argentina", "Paraguay", "Uruguay"
]

def read_names_from_file(file_path: str) -> List[str]:
    """Read names from the Hispanic names file."""
    names = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if line and not line.startswith('#'):
                    names.append(line)
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        return []
    except Exception as e:
        print(f"Error reading file {file_path}: {str(e)}")
        return []
    return names

def parse_full_name(full_name: str) -> tuple:
    """Parse a full name into first and last name components."""
    parts = full_name.split()
    if len(parts) >= 2:
        return parts[0], " ".join(parts[1:])  # First name and last name (including compound names)
    else:
        return full_name, ""  # Handle edge cases

class HispanicNameSearcher:
    """Class to search Hispanic names using ICE Locator MCP Server."""
    
    def __init__(self, output_csv: str = "hispanic_names_search_results.csv"):
        """Initialize the searcher."""
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
        
        # Create or overwrite the CSV file with headers
        with open(self.output_csv, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
    
    def _append_to_csv(self, result_data: Dict[str, Any]):
        """Append a result to the CSV file."""
        headers = [
            "full_name", "first_name", "last_name", "alien_number", 
            "date_of_birth", "country_of_birth", "facility_name", 
            "facility_location", "custody_status", "last_updated", "search_timestamp"
        ]
        
        with open(self.output_csv, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writerow(result_data)
    
    async def search_name_with_mcp(self, client_session, full_name: str) -> Optional[Dict]:
        """
        Search for a detainee by full name using the MCP server.
        
        Args:
            client_session: MCP client session
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
        country = "Mexico"  # Default country for search
        
        try:
            # Call the MCP tool for searching by name
            print(f"Searching for: {full_name}")
            response = await client_session.call_tool(
                name="search_detainee_by_name",
                arguments={
                    "first_name": first_name,
                    "last_name": last_name,
                    "date_of_birth": SAMPLE_DOB,
                    "country_of_birth": country
                }
            )
            
            self.processed_count += 1
            print(f"Processed {self.processed_count} names...")
            
            # Check if we found a match
            if response.content and len(response.content) > 0:
                result_content = response.content[0].text
                if result_content:
                    try:
                        result_data = json.loads(result_content)
                        if result_data.get("status") == "found" and result_data.get("results"):
                            self.found_count += 1
                            print(f"Found match for {full_name}!")
                            return {
                                "full_name": full_name,
                                "first_name": first_name,
                                "last_name": last_name,
                                "search_result": result_data
                            }
                    except json.JSONDecodeError:
                        print(f"Error parsing response for {full_name}: {result_content}")
            else:
                print(f"No match found for {full_name}")
                
        except Exception as e:
            print(f"Error searching for {full_name}: {str(e)}")
            
        return None
    
    async def process_search_results(self, result: Dict[str, Any]):
        """Process search results and write to CSV."""
        if not result or "search_result" not in result:
            return
            
        search_result = result["search_result"]
        if search_result.get("status") == "found" and search_result.get("results"):
            for detainee in search_result["results"]:
                csv_data = {
                    "full_name": result["full_name"],
                    "first_name": result["first_name"],
                    "last_name": result["last_name"],
                    "alien_number": detainee.get("alien_number", ""),
                    "date_of_birth": detainee.get("date_of_birth", ""),
                    "country_of_birth": detainee.get("country_of_birth", ""),
                    "facility_name": detainee.get("facility_name", ""),
                    "facility_location": detainee.get("facility_location", ""),
                    "custody_status": detainee.get("custody_status", ""),
                    "last_updated": detainee.get("last_updated", ""),
                    "search_timestamp": datetime.now().isoformat()
                }
                self._append_to_csv(csv_data)
                self.results_count += 1
    
    async def search_names_batch(self, names: List[str], batch_size: int = 3, delay: float = 2.0):
        """
        Search for names in batches using the MCP server.
        
        Args:
            names: List of names to search for
            batch_size: Number of concurrent searches
            delay: Delay between batches in seconds
        """
        print(f"Processing {len(names)} names in batches of {batch_size}")
        
        # Start the MCP server using stdio transport with configuration
        server_params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "ice_locator_mcp"],
            cwd=os.path.join(os.path.dirname(__file__)),
            env={
                **os.environ,
                "ICE_LOCATOR_CONFIG": "config/production.json",
                "ICE_LOCATOR_ANALYTICS_ENABLED": "false"
            }
        )
        
        try:
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    # List available tools
                    try:
                        tools = await session.list_tools()
                        print(f"Available tools: {[tool.name for tool in tools]}")
                    except Exception as e:
                        print(f"Error listing tools: {e}")
                        return
                    
                    # Process names in batches
                    for i in range(0, len(names), batch_size):
                        batch = names[i:i + batch_size]
                        print(f"\nProcessing batch {i//batch_size + 1}/{(len(names)-1)//batch_size + 1}")
                        
                        # Create tasks for concurrent searches
                        tasks = [self.search_name_with_mcp(session, name) for name in batch]
                        results = await asyncio.gather(*tasks, return_exceptions=True)
                        
                        # Process results
                        for result in results:
                            if isinstance(result, Exception):
                                print(f"Error in search: {result}")
                            else:
                                await self.process_search_results(result)
                        
                        # Add delay between batches
                        if i + batch_size < len(names):
                            print(f"Waiting {delay} seconds before next batch...")
                            await asyncio.sleep(delay)
        except Exception as e:
            print(f"Error connecting to MCP server: {e}")

    def print_summary(self):
        """Print a summary of the search results."""
        print("\n" + "="*50)
        print("SEARCH SUMMARY")
        print("="*50)
        print(f"Total names processed: {self.processed_count}")
        print(f"Matches found: {self.found_count}")
        print(f"Results written to CSV: {self.results_count}")
        print(f"Output file: {self.output_csv}")
        print("="*50)

async def main():
    """Main function to search all Hispanic names."""
    print("Starting search of Hispanic/Latino names using ICE Locator MCP...")
    
    # Read names from file
    names_file = "hispanic_names_data/organized/hispanic_full_names_huge.txt"
    print(f"Reading names from {names_file}...")
    names = read_names_from_file(names_file)
    
    if not names:
        print("No names found to search. Exiting.")
        return
    
    print(f"Found {len(names)} names to search.")
    
    # For testing purposes, let's limit to a smaller sample
    # In a real scenario, you would process all names
    sample_size = min(50, len(names))  # Process up to 50 names for testing
    sample_names = names[:sample_size]
    print(f"Processing sample of {sample_size} names...")
    
    # Create searcher instance
    searcher = HispanicNameSearcher("hispanic_names_search_results.csv")
    
    # Process names
    try:
        await searcher.search_names_batch(sample_names, batch_size=3, delay=1.0)
    except KeyboardInterrupt:
        print("\nSearch interrupted by user.")
    except Exception as e:
        print(f"\nError during search: {e}")
    
    # Print summary
    searcher.print_summary()

if __name__ == "__main__":
    asyncio.run(main())