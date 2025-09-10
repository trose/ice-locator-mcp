#!/usr/bin/env python3
"""
Search for 10 Hispanic names using the ICE Locator MCP Server via HTTP with proper session handling.
"""

import asyncio
import csv
import json
import os
import random
import httpx
from datetime import datetime
from typing import Dict, List, Optional


class HispanicNamesHTTPClient:
    """HTTP client for searching Hispanic names using the ICE Locator MCP Server with session handling."""
    
    def __init__(self, server_url: str = "http://127.0.0.1:8081/mcp", output_csv: str = "hispanic_names_session_results.csv"):
        """Initialize the HTTP client."""
        self.server_url = server_url
        self.output_csv = output_csv
        self.session_id = None
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
    
    async def initialize_session(self, client: httpx.AsyncClient) -> bool:
        """Initialize a session with the MCP server."""
        try:
            # Make an initial request to get a session ID
            response = await client.post(
                self.server_url,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/list",
                    "params": {}
                },
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream"
                }
            )
            
            # Extract session ID from headers
            self.session_id = response.headers.get('mcp-session-id')
            if self.session_id:
                print(f"Session initialized with ID: {self.session_id}")
                return True
            else:
                print("Failed to get session ID from server")
                return False
                
        except Exception as e:
            print(f"Error initializing session: {str(e)}")
            return False
    
    async def list_tools(self, client: httpx.AsyncClient) -> List[str]:
        """List available tools from the MCP server."""
        if not self.session_id:
            print("No session ID available")
            return []
            
        try:
            response = await client.post(
                self.server_url,
                json={
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/list",
                    "params": {}
                },
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream",
                    "mcp-session-id": self.session_id
                }
            )
            
            if response.status_code == 200:
                # Parse the response
                response_text = response.text
                if response_text.startswith("event: message\ndata: "):
                    json_data = response_text[22:]  # Remove "event: message\ndata: " prefix
                    data = json.loads(json_data)
                    if "result" in data:
                        tools = data["result"]
                        return [tool["name"] for tool in tools]
                print(f"Error parsing tools list response: {response_text}")
            else:
                print(f"Error listing tools: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error listing tools: {e}")
        return []
    
    async def search_name_via_http(self, client: httpx.AsyncClient, full_name: str) -> Optional[Dict]:
        """
        Search for a detainee by full name using the HTTP MCP server with session handling.
        
        Args:
            client: HTTP client for making requests
            full_name: Full name in format "FirstName LastName"
            
        Returns:
            Dictionary with search results or None if no results
        """
        if not self.session_id:
            print("No session ID available")
            return None
            
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
        
        # Prepare the tool call
        tool_call = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "search_detainee_by_name",
                "arguments": {
                    "first_name": first_name,
                    "last_name": last_name,
                    "date_of_birth": date_of_birth,
                    "country_of_birth": country_of_birth
                }
            }
        }
        
        try:
            print(f"Searching for: {full_name} ({date_of_birth}, {country_of_birth})")
            
            # Make the HTTP request to the MCP server
            response = await client.post(
                self.server_url,
                json=tool_call,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream",
                    "mcp-session-id": self.session_id
                }
            )
            
            # Process the response
            if response.status_code == 200:
                # Parse the response
                response_text = response.text
                if response_text.startswith("event: message\ndata: "):
                    json_data = response_text[22:]  # Remove "event: message\ndata: " prefix
                    result_data = json.loads(json_data)
                    if "result" in result_data:
                        return result_data["result"]
                    else:
                        print(f"No result in response for {full_name}: {result_data}")
                        return None
                else:
                    print(f"Unexpected response format for {full_name}: {response_text}")
                    return None
            else:
                print(f"HTTP error {response.status_code} for {full_name}: {response.text}")
                return None
                
        except Exception as e:
            print(f"Error searching for {full_name}: {str(e)}")
            return None
    
    async def run_search(self, input_file: str):
        """
        Run the search process for exactly 10 names from the input file.
        """
        print(f"Starting HTTP search for 10 Hispanic names from {input_file}")
        print(f"Results will be saved to {self.output_csv}")
        
        # Read the first 10 names from file
        names = self.read_first_10_names(input_file)
        
        if not names:
            print("No names found in the input file.")
            return
        
        print(f"Found {len(names)} names to search for.")
        
        # Create HTTP client
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Initialize session
            if not await self.initialize_session(client):
                print("Failed to initialize session with server")
                return
            
            # List available tools
            tools = await self.list_tools(client)
            if tools:
                print(f"Available tools: {tools}")
            else:
                print("Failed to list tools")
            
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
                
                # Search for the name using HTTP
                result = await self.search_name_via_http(client, name)
                
                # Save the result
                if result:
                    self.save_result(name, first_name, last_name, country_of_birth, date_of_birth, result)
                
                self.processed_count += 1
                print(f"Progress: {self.processed_count}/10 names processed, Found: {self.found_count} matches")
            
            print(f"\n--- Search Complete ---")
            print(f"Total names processed: {self.processed_count}")
            print(f"Matches found: {self.found_count}")
            print(f"Results saved to: {self.output_csv}")


async def main():
    """Main function to run the search for 10 Hispanic names via HTTP with session handling."""
    # Initialize the searcher
    searcher = HispanicNamesHTTPClient("http://127.0.0.1:8081/mcp", "hispanic_names_session_results.csv")
    
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
    asyncio.run(main())