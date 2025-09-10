#!/usr/bin/env python3
"""
Direct test of the search functionality without MCP server.
"""

import asyncio
import csv
import json
import os
import random
import sys
from datetime import datetime
from typing import Dict, List

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ice_locator_mcp.core.search_engine import SearchEngine
from ice_locator_mcp.anti_detection.proxy_manager import ProxyManager
from ice_locator_mcp.core.config import ServerConfig

class DirectSearchTest:
    """Direct test of search functionality."""
    
    def __init__(self):
        """Initialize the test."""
        self.config = ServerConfig()
        self.proxy_manager = ProxyManager(self.config.proxy_config)
        self.search_engine = SearchEngine(
            proxy_manager=self.proxy_manager,
            config=self.config.search_config
        )
        
        # Hispanic countries for testing
        self.hispanic_countries = [
            "Mexico", "Guatemala", "El Salvador", "Honduras", "Nicaragua", 
            "Costa Rica", "Panama", "Colombia", "Venezuela", "Ecuador",
            "Peru", "Bolivia", "Chile", "Argentina", "Paraguay", "Uruguay",
            "Cuba", "Dominican Republic", "Puerto Rico"
        ]
    
    def generate_realistic_dob(self) -> str:
        """Generate a realistic date of birth (between 18-65 years old)."""
        age = random.randint(18, 65)
        current_year = datetime.now().year
        birth_year = current_year - age
        birth_month = random.randint(1, 12)
        birth_day = 15
        return f"{birth_year}-{birth_month:02d}-{birth_day:02d}"
    
    def generate_country_of_birth(self) -> str:
        """Generate a realistic country of birth."""
        return random.choice(self.hispanic_countries)
    
    def read_first_10_names(self, filename: str) -> List[str]:
        """Read the first 10 names from the file."""
        names = []
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        names.append(line)
                        if len(names) >= 10:
                            break
        except FileNotFoundError:
            print(f"Error: File {filename} not found.")
        except Exception as e:
            print(f"Error reading file {filename}: {str(e)}")
        
        return names
    
    async def test_search(self, first_name: str, last_name: str, 
                         date_of_birth: str, country_of_birth: str) -> Dict:
        """Test a single search."""
        try:
            print(f"Searching for: {first_name} {last_name} ({date_of_birth}, {country_of_birth})")
            
            # Use the search engine directly
            result = await self.search_engine.search_detainee_by_name(
                first_name=first_name,
                last_name=last_name,
                date_of_birth=date_of_birth,
                country_of_birth=country_of_birth,
                fuzzy_search=True
            )
            
            return result
            
        except Exception as e:
            print(f"Error searching for {first_name} {last_name}: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def run_test(self, input_file: str, output_csv: str = "direct_search_results.csv"):
        """Run the direct search test."""
        print(f"Starting direct search test from {input_file}")
        print(f"Results will be saved to {output_csv}")
        
        # Initialize components
        await self.proxy_manager.initialize()
        await self.search_engine.initialize()
        
        # Read names
        names = self.read_first_10_names(input_file)
        if not names:
            print("No names found in the input file.")
            return
        
        print(f"Found {len(names)} names to search for.")
        
        # Initialize CSV file
        headers = [
            "full_name", "first_name", "last_name", "date_of_birth", 
            "country_of_birth", "status", "results", "search_timestamp"
        ]
        
        with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
        
        # Process each name
        found_count = 0
        for i, name in enumerate(names, 1):
            print(f"\n--- Processing name {i}/10 ---")
            
            parts = name.strip().split()
            if len(parts) < 2:
                print(f"Skipping invalid name: {name}")
                continue
            
            first_name = parts[0]
            last_name = " ".join(parts[1:])
            date_of_birth = self.generate_realistic_dob()
            country_of_birth = self.generate_country_of_birth()
            
            # Test the search
            result = await self.test_search(first_name, last_name, date_of_birth, country_of_birth)
            
            # Save result
            row = [
                name,
                first_name,
                last_name,
                date_of_birth,
                country_of_birth,
                result.get("status", "unknown"),
                json.dumps(result.get("results", [])),
                datetime.now().isoformat()
            ]
            
            with open(output_csv, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(row)
            
            if result.get("status") == "found":
                found_count += 1
                print(f"Found result for: {name}")
            else:
                print(f"No results found for: {name}")
        
        print(f"\n--- Test Complete ---")
        print(f"Total names processed: {len(names)}")
        print(f"Matches found: {found_count}")
        print(f"Results saved to: {output_csv}")
        
        # Cleanup
        await self.search_engine.cleanup()
        await self.proxy_manager.cleanup()

async def main():
    """Main function."""
    test = DirectSearchTest()
    
    # Input file path
    input_file = "hispanic_names_data/organized/hispanic_full_names_huge.txt"
    full_path = os.path.join(os.path.dirname(__file__), input_file)
    
    # Check if input file exists
    if not os.path.exists(full_path):
        print(f"Error: Input file {full_path} not found.")
        return
    
    # Run the test
    await test.run_test(full_path)

if __name__ == "__main__":
    asyncio.run(main())

