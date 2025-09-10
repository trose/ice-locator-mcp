#!/usr/bin/env python3
"""
Demonstration of proper MCP usage for searching Hispanic names.

This script shows how to follow the instructions in hispanic_names_data/MCP_SEARCH_INSTRUCTIONS.md
for searching 10 names from hispanic_names_data/organized/hispanic_full_names_huge.txt
"""

import json
import random
from datetime import datetime
from typing import Dict, List


class MCPInstructionsDemo:
    """Demonstration of MCP usage following the instructions."""
    
    def __init__(self):
        """Initialize the demo."""
        self.hispanic_countries = [
            "Mexico", "Guatemala", "El Salvador", "Honduras", "Nicaragua", 
            "Costa Rica", "Panama", "Colombia", "Venezuela", "Ecuador",
            "Peru", "Bolivia", "Chile", "Argentina", "Paraguay", "Uruguay",
            "Cuba", "Dominican Republic", "Puerto Rico"
        ]
    
    def read_first_10_names(self, filename: str) -> List[str]:
        """Read the first 10 names from the file."""
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
    
    def demonstrate_search_detainee_by_name(self, first_name: str, last_name: str, 
                                          date_of_birth: str, country_of_birth: str) -> Dict:
        """
        Demonstrate the proper usage of search_detainee_by_name tool as per instructions.
        
        This follows the exact format specified in MCP_SEARCH_INSTRUCTIONS.md
        """
        # This is how you would call the MCP tool according to the instructions
        tool_call = {
            "name": "search_detainee_by_name",
            "arguments": {
                "first_name": first_name,
                "last_name": last_name,
                "date_of_birth": date_of_birth,
                "country_of_birth": country_of_birth
            }
        }
        
        print(f"MCP Tool Call: {json.dumps(tool_call, indent=2)}")
        
        # This is what a successful response would look like according to the instructions
        sample_response = {
            "status": "found",
            "results": [
                {
                    "first_name": first_name,
                    "last_name": last_name,
                    "alien_number": f"A{random.randint(100000000, 999999999)}",
                    "date_of_birth": date_of_birth,
                    "country_of_birth": country_of_birth,
                    "facility_name": "Sample Detention Facility",
                    "facility_location": "Sample City, State",
                    "custody_status": "In Detention",
                    "last_updated": datetime.now().isoformat()
                }
            ]
        }
        
        return sample_response
    
    def demonstrate_bulk_search(self, names: List[str]) -> List[Dict]:
        """
        Demonstrate the proper usage of bulk_search_detainees tool as per instructions.
        
        This follows the exact format specified in MCP_SEARCH_INSTRUCTIONS.md
        """
        search_requests = []
        for name in names[:3]:  # Demonstrate with first 3 names
            parts = name.strip().split()
            if len(parts) >= 2:
                first_name = parts[0]
                last_name = " ".join(parts[1:])
                date_of_birth = self.generate_realistic_dob()
                country_of_birth = self.generate_country_of_birth()
                
                search_requests.append({
                    "first_name": first_name,
                    "last_name": last_name,
                    "date_of_birth": date_of_birth,
                    "country_of_birth": country_of_birth
                })
        
        # This is how you would call the MCP tool according to the instructions
        tool_call = {
            "name": "bulk_search_detainees",
            "arguments": {
                "search_requests": search_requests,
                "max_concurrent": 3,
                "continue_on_error": True
            }
        }
        
        print(f"Bulk Search MCP Tool Call: {json.dumps(tool_call, indent=2)}")
        
        # Return sample responses
        responses = []
        for req in search_requests:
            responses.append({
                "status": "found",
                "results": [
                    {
                        "first_name": req["first_name"],
                        "last_name": req["last_name"],
                        "alien_number": f"A{random.randint(100000000, 999999999)}",
                        "date_of_birth": req["date_of_birth"],
                        "country_of_birth": req["country_of_birth"],
                        "facility_name": "Sample Detention Facility",
                        "facility_location": "Sample City, State",
                        "custody_status": "In Detention",
                        "last_updated": datetime.now().isoformat()
                    }
                ]
            })
        
        return responses
    
    def run_demo(self, input_file: str):
        """Run the demonstration of MCP usage."""
        print("=== MCP Usage Demonstration ===")
        print("Following instructions from hispanic_names_data/MCP_SEARCH_INSTRUCTIONS.md")
        print()
        
        # Read the first 10 names
        names = self.read_first_10_names(input_file)
        
        if not names:
            print("No names found in the input file.")
            return
        
        print(f"Found {len(names)} names to demonstrate with:")
        for i, name in enumerate(names, 1):
            print(f"  {i}. {name}")
        print()
        
        print("=== Individual Search Demonstrations ===")
        # Demonstrate individual searches
        for i, name in enumerate(names[:3], 1):  # Demonstrate with first 3 names
            print(f"\n--- Search {i} ---")
            parts = name.strip().split()
            if len(parts) >= 2:
                first_name = parts[0]
                last_name = " ".join(parts[1:])
                date_of_birth = self.generate_realistic_dob()
                country_of_birth = self.generate_country_of_birth()
                
                print(f"Name: {name}")
                print(f"Generated DOB: {date_of_birth}")
                print(f"Generated Country: {country_of_birth}")
                
                # Demonstrate the proper MCP tool call
                response = self.demonstrate_search_detainee_by_name(
                    first_name, last_name, date_of_birth, country_of_birth
                )
                
                print(f"Sample Response: {json.dumps(response, indent=2)}")
        
        print("\n=== Bulk Search Demonstration ===")
        # Demonstrate bulk search
        bulk_responses = self.demonstrate_bulk_search(names)
        
        print(f"\nSample Bulk Responses: {json.dumps(bulk_responses, indent=2)}")
        
        print("\n=== Key Points from MCP_SEARCH_INSTRUCTIONS.md ===")
        print("1. Always use the exact tool names: search_detainee_by_name, search_detainee_by_alien_number, etc.")
        print("2. Provide all required parameters: first_name, last_name, date_of_birth, country_of_birth")
        print("3. Handle all response types: 'found', 'not_found', and 'error'")
        print("4. Extract key information: name, alien_number, date_of_birth, country_of_birth, facility_name, facility_location, custody_status, last_updated")
        print("5. Never call the ICE website directly; always use MCP tools to avoid 403 errors")


def main():
    """Main function to run the MCP usage demonstration."""
    demo = MCPInstructionsDemo()
    
    # Input file path
    input_file = "hispanic_names_data/organized/hispanic_full_names_huge.txt"
    full_path = f"/Users/trose/src/locator-mcp/{input_file}"
    
    # Run the demonstration
    demo.run_demo(full_path)


if __name__ == "__main__":
    main()