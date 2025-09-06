#!/usr/bin/env python3
"""
Search Hispanic/Latino names using the ICE Locator MCP Server and generate CSV results.

This script properly uses the MCP protocol to communicate with the server,
avoiding the 403 errors we encountered with direct API calls.
"""

import asyncio
import csv
import json
import os
import sys
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

# Add the src directory to the path so we can import the MCP components
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class HispanicNameMCPSearcher:
    """MCP client for searching Hispanic/Latino names in the ICE database."""
    
    def __init__(self, output_csv: str = "hispanic_names_mcp_results.csv"):
        """Initialize the MCP name searcher."""
        self.output_csv = output_csv
        self.results_count = 0
        self.processed_count = 0
        self.found_count = 0
        
        # Common Hispanic countries for country of birth
        self.hispanic_countries = [
            "Mexico", "Guatemala", "El Salvador", "Honduras", "Nicaragua", 
            "Costa Rica", "Panama", "Colombia", "Venezuela", "Ecuador",
            "Peru", "Bolivia", "Chile", "Argentina", "Paraguay", "Uruguay",
            "Cuba", "Dominican Republic", "Puerto Rico"
        ]
        
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
    
    def save_result(self, full_name: str, first_name: str, last_name: str, 
                   country_of_birth: str, date_of_birth: str, result: Dict):
        """Save a single result to the CSV file."""
        if result and result.get("status") == "found" and result.get("results"):
            detainee = result["results"][0]
            row = [
                full_name,
                first_name,
                last_name,
                detainee.get("alien_number", ""),
                date_of_birth,
                country_of_birth,
                detainee.get("facility_name", ""),
                detainee.get("facility_location", ""),
                detainee.get("custody_status", ""),
                detainee.get("last_updated", ""),
                datetime.now().isoformat()
            ]
            
            with open(self.output_csv, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(row)
            
            self.found_count += 1
            print(f"Found result for: {full_name} - {detainee.get('custody_status', 'Unknown')} at {detainee.get('facility_name', 'Unknown')}")
    
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
    
    def generate_realistic_dob(self) -> str:
        """Generate a realistic date of birth (between 18-65 years old)."""
        # Generate a random age between 18 and 65
        age = random.randint(18, 65)
        # Calculate birth year
        current_year = datetime.now().year
        birth_year = current_year - age
        
        # Generate random month and day
        birth_month = random.randint(1, 12)
        # For simplicity, use 15 as day to avoid month-specific issues
        birth_day = 15
        
        return f"{birth_year}-{birth_month:02d}-{birth_day:02d}"
    
    def generate_country_of_birth(self) -> str:
        """Generate a realistic country of birth from common Hispanic countries."""
        return random.choice(self.hispanic_countries)
    
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
        
        # Generate realistic date of birth and country of birth
        date_of_birth = self.generate_realistic_dob()
        country_of_birth = self.generate_country_of_birth()
        
        try:
            # Call the MCP tool for searching by name
            print(f"Searching for: {full_name} ({date_of_birth}, {country_of_birth})")
            response = await client_session.call_tool(
                name="search_detainee_by_name",
                arguments={
                    "first_name": first_name,
                    "last_name": last_name,
                    "date_of_birth": date_of_birth,
                    "country_of_birth": country_of_birth
                }
            )
            
            # Process the response
            if response and response.content:
                # The response content is a list of TextContent objects
                for content_item in response.content:
                    if hasattr(content_item, 'text'):
                        try:
                            result_data = json.loads(content_item.text)
                            return result_data
                        except json.JSONDecodeError:
                            print(f"Could not parse response for {full_name}: {content_item.text}")
                            return None
            else:
                print(f"No response content for {full_name}")
                return None
                
        except Exception as e:
            print(f"Error searching for {full_name}: {str(e)}")
            return None
    
    async def search_names_batch(self, names: List[str], batch_size: int = 3, delay: float = 2.0):
        """
        Search for names in batches using the MCP server.
        
        Args:
            names: List of names to search for
            batch_size: Number of concurrent searches
            delay: Delay between batches in seconds
        """
        print(f"Processing {len(names)} names in batches of {batch_size}")
        
        # Start the MCP server using stdio transport
        server_params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "ice_locator_mcp"],
            cwd=os.path.join(os.path.dirname(__file__))
        )
        
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
                    
                    # Process each name in the batch
                    for name in batch:
                        # Parse the full name
                        parts = name.strip().split()
                        if len(parts) < 2:
                            print(f"Skipping invalid name: {name}")
                            self.processed_count += 1
                            continue
                            
                        first_name = parts[0]
                        last_name = " ".join(parts[1:])  # Handle compound last names
                        
                        # Generate realistic date of birth and country of birth
                        date_of_birth = self.generate_realistic_dob()
                        country_of_birth = self.generate_country_of_birth()
                        
                        result = await self.search_name_with_mcp(session, name)
                        if result:
                            self.save_result(name, first_name, last_name, country_of_birth, date_of_birth, result)
                        
                        self.processed_count += 1
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
        print(f"Starting MCP search process for names in {input_file}")
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
            import traceback
            traceback.print_exc()
        
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
    import argparse
    
    parser = argparse.ArgumentParser(description='Search Hispanic names using ICE Locator MCP')
    parser.add_argument('--input', default='hispanic_names_data/organized/hispanic_full_names_extended_huge.txt',
                       help='Input file with names to search')
    parser.add_argument('--output', default='hispanic_names_mcp_results.csv',
                       help='Output CSV file for results')
    parser.add_argument('--max-names', type=int, default=None,
                       help='Maximum number of names to process (default: all)')
    
    args = parser.parse_args()
    
    # Initialize the searcher
    searcher = HispanicNameMCPSearcher(args.output)
    
    # Input file path
    full_path = os.path.join(os.path.dirname(__file__), args.input)
    
    # Check if input file exists
    if not os.path.exists(full_path):
        print(f"Error: Input file {full_path} not found.")
        return
    
    # Run the search
    await searcher.run_search(full_path, max_names=args.max_names)


if __name__ == "__main__":
    asyncio.run(main())