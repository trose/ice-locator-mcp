#!/usr/bin/env python3
"""
Search for 10 Hispanic names using the ICE Locator MCP Server following the instructions.

This script demonstrates proper MCP tool usage as described in hispanic_names_data/MCP_SEARCH_INSTRUCTIONS.md
"""

import asyncio
import csv
import json
import os
import sys
import random
from datetime import datetime
from typing import Dict, List, Optional

# Add the src directory to the path so we can import the MCP components
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    MCP_AVAILABLE = True
except ImportError:
    print("MCP library not available. Please install it with: pip install mcp")
    MCP_AVAILABLE = False


class HispanicNamesMCPClient:
    """MCP client for searching exactly 10 Hispanic names as instructed."""
    
    def __init__(self, output_csv: str = "hispanic_names_10_results.csv"):
        """Initialize the MCP client."""
        self.output_csv = output_csv
        self.found_count = 0
        self.processed_count = 0
        
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
        elif result and result.get("status") == "not_found":
            print(f"No results found for: {full_name}")
        else:
            print(f"Error searching for: {full_name}")
    
    def read_first_10_names(self, filename: str) -> List[str]:
        """Read the first 10 names from the file, skipping comment lines."""
        names = []
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comment lines
                    if line and not line.startswith('#'):
                        names.append(line)
                        # Stop after getting 10 names
                        if len(names) >= 10:
                            break
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
        
        Following the instructions in hispanic_names_data/MCP_SEARCH_INSTRUCTIONS.md:
        - Using the search_detainee_by_name tool
        - Providing first_name, last_name, date_of_birth, and country_of_birth
        
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
    
    async def run_search(self, input_file: str):
        """
        Run the search process for exactly 10 names from the input file.
        
        Following the instructions in hispanic_names_data/MCP_SEARCH_INSTRUCTIONS.md
        """
        if not MCP_AVAILABLE:
            print("Cannot run search without MCP library.")
            return
            
        print(f"Starting MCP search for 10 Hispanic names from {input_file}")
        print(f"Results will be saved to {self.output_csv}")
        
        # Read the first 10 names from file
        names = self.read_first_10_names(input_file)
        
        if not names:
            print("No names found in the input file.")
            return
        
        print(f"Found {len(names)} names to search for.")
        
        # Start the MCP server using stdio transport
        server_params = StdioServerParameters(
            command=os.path.join(os.path.dirname(__file__), ".venv", "bin", "python"),
            args=["-m", "ice_locator_mcp"],
            cwd=os.path.join(os.path.dirname(__file__)),
            env={
                "PYTHONPATH": os.path.join(os.path.dirname(__file__), "src")
            }
        )
        
        try:
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    # List available tools to verify connection
                    try:
                        tools = await session.list_tools()
                        print(f"Connected to MCP server. Available tools: {[tool.name for tool in tools]}")
                    except Exception as e:
                        print(f"Error connecting to MCP server: {e}")
                        return
                    
                    # Process each name
                    for i, name in enumerate(names, 1):
                        print(f"\n--- Processing name {i}/10 ---")
                        
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
                        
                        # Search for the name using MCP
                        result = await self.search_name_with_mcp(session, name)
                        
                        # Save the result
                        if result:
                            self.save_result(name, first_name, last_name, country_of_birth, date_of_birth, result)
                        
                        self.processed_count += 1
                        print(f"Progress: {self.processed_count}/10 names processed, Found: {self.found_count} matches")
                    
                    print(f"\n--- Search Complete ---")
                    print(f"Total names processed: {self.processed_count}")
                    print(f"Matches found: {self.found_count}")
                    print(f"Results saved to: {self.output_csv}")
        except Exception as e:
            print(f"Error connecting to MCP server: {e}")
            print("Please make sure the ICE Locator MCP server is properly installed and configured.")


async def main():
    """Main function to run the search for 10 Hispanic names."""
    if not MCP_AVAILABLE:
        print("MCP library not available. Please install it with: pip install mcp")
        return
        
    # Initialize the searcher
    searcher = HispanicNamesMCPClient("hispanic_names_10_results.csv")
    
    # Input file path - using the huge file as specified
    input_file = "hispanic_names_data/organized/hispanic_full_names_huge.txt"
    full_path = os.path.join(os.path.dirname(__file__), input_file)
    
    # Check if input file exists
    if not os.path.exists(full_path):
        print(f"Error: Input file {full_path} not found.")
        return
    
    # Run the search for exactly 10 names
    await searcher.run_search(full_path)


if __name__ == "__main__":
    if MCP_AVAILABLE:
        asyncio.run(main())
    else:
        print("MCP library not available. Please install it with: pip install mcp")