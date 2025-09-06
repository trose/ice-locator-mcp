#!/usr/bin/env python3
"""
Direct search of Hispanic names using the MCP server via HTTP.
"""

import csv
import json
import random
import asyncio
import httpx
from datetime import datetime
from typing import List


def read_names_from_file(filename: str) -> List[str]:
    """Read names from the file, skipping comment lines."""
    names = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comment lines
            if line and not line.startswith('#'):
                names.append(line)
    return names


def generate_realistic_dob() -> str:
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


def generate_country_of_birth() -> str:
    """Generate a realistic country of birth from common Hispanic countries."""
    hispanic_countries = [
        "Mexico", "Guatemala", "El Salvador", "Honduras", "Nicaragua", 
        "Costa Rica", "Panama", "Colombia", "Venezuela", "Ecuador",
        "Peru", "Bolivia", "Chile", "Argentina", "Paraguay", "Uruguay",
        "Cuba", "Dominican Republic", "Puerto Rico"
    ]
    return random.choice(hispanic_countries)


def initialize_csv(output_csv: str):
    """Initialize the CSV file with headers."""
    headers = [
        "full_name", "first_name", "last_name", "alien_number", 
        "date_of_birth", "country_of_birth", "facility_name", 
        "facility_location", "custody_status", "last_updated", "search_timestamp"
    ]
    
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
    print(f"Initialized CSV file: {output_csv}")


def save_result(output_csv: str, full_name: str, first_name: str, last_name: str, 
               country_of_birth: str, date_of_birth: str, result: dict):
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
        
        with open(output_csv, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(row)
        
        print(f"Found result for: {full_name} - {detainee.get('custody_status', 'Unknown')} at {detainee.get('facility_name', 'Unknown')}")
        return True
    return False


async def search_name_with_mcp_http(client, full_name: str, output_csv: str):
    """Search for a name using the MCP server via HTTP and save results."""
    # Parse the full name
    parts = full_name.strip().split()
    if len(parts) < 2:
        print(f"Skipping invalid name: {full_name}")
        return False
        
    first_name = parts[0]
    last_name = " ".join(parts[1:])  # Handle compound last names
    
    # Generate realistic date of birth and country of birth
    date_of_birth = generate_realistic_dob()
    country_of_birth = generate_country_of_birth()
    
    try:
        print(f"Searching for: {full_name} ({date_of_birth}, {country_of_birth})")
        
        # Call the MCP tool for searching by name via HTTP
        response = await client.post(
            "http://localhost:8080/mcp",
            json={
                "method": "call_tool",
                "params": {
                    "name": "search_detainee_by_name",
                    "arguments": {
                        "first_name": first_name,
                        "last_name": last_name,
                        "date_of_birth": date_of_birth,
                        "country_of_birth": country_of_birth
                    }
                }
            },
            headers={"Content-Type": "application/json"}
        )
        
        # Process the response
        result_data = None
        if response.status_code == 200:
            try:
                response_data = response.json()
                if "result" in response_data and "content" in response_data["result"]:
                    content = response_data["result"]["content"]
                    if content and len(content) > 0 and "text" in content[0]:
                        result_data = json.loads(content[0]["text"])
            except json.JSONDecodeError:
                print(f"Could not parse response for {full_name}: {response.text}")
            except Exception as e:
                print(f"Error processing response for {full_name}: {str(e)}")
        else:
            print(f"HTTP error {response.status_code} for {full_name}: {response.text}")
        
        # Save result if found
        if save_result(output_csv, full_name, first_name, last_name, country_of_birth, date_of_birth, result_data):
            return True
            
    except Exception as e:
        print(f"Error searching for {full_name}: {str(e)}")
    
    return False


async def main():
    """Main function to search names and generate CSV."""
    input_file = "hispanic_names_data/organized/hispanic_full_names_huge.txt"
    output_csv = "hispanic_names_search_results_http.csv"
    
    print(f"Reading names from {input_file}")
    names = read_names_from_file(input_file)
    print(f"Found {len(names)} names in the input file.")
    
    # Initialize CSV file
    initialize_csv(output_csv)
    
    # Process all names
    print(f"Processing all {len(names)} names")
    
    found_count = 0
    processed_count = 0
    
    # Create HTTP client
    async with httpx.AsyncClient() as client:
        # Process names in batches to avoid overwhelming the server
        batch_size = 5
        delay_between_batches = 2.0
        
        for i in range(0, len(names), batch_size):
            batch = names[i:i + batch_size]
            print(f"\nProcessing batch {i//batch_size + 1}/{(len(names)-1)//batch_size + 1}")
            
            # Process each name in the batch
            for name in batch:
                if await search_name_with_mcp_http(client, name, output_csv):
                    found_count += 1
                processed_count += 1
                
                print(f"Processed: {processed_count}/{len(names)} names, Found: {found_count} matches")
            
            # Delay between batches
            if i + batch_size < len(names):
                print(f"Waiting {delay_between_batches} seconds before next batch...")
                await asyncio.sleep(delay_between_batches)
    
    print(f"\nSearch completed!")
    print(f"Total names processed: {processed_count}")
    print(f"Matches found: {found_count}")
    print(f"Results saved to: {output_csv}")


if __name__ == "__main__":
    asyncio.run(main())