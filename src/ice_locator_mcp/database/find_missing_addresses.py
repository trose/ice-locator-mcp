"""
Script to find addresses for agencies that failed to geocode.
"""
import os
import sys
import csv
import time
import requests
from urllib.parse import quote_plus

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def search_web_for_address(agency_name: str, state: str) -> str:
    """
    Search the web for an address for the given agency.
    
    Args:
        agency_name: Name of the law enforcement agency
        state: State abbreviation or full name
        
    Returns:
        Found address or empty string
    """
    # Clean up the agency name
    search_query = f"{agency_name} {state} official website"
    
    try:
        # Using a simple web search approach
        # In a real implementation, we would use a proper search API
        print(f"Searching for: {search_query}")
        
        # For now, we'll return a placeholder - in a real implementation
        # we would use a search API like Google Custom Search or similar
        return ""
        
    except Exception as e:
        print(f"Error searching for {agency_name}: {e}")
        return ""

def find_addresses_for_missing_agencies(csv_file_path: str, output_file_path: str = None):
    """
    Find addresses for agencies that failed to geocode.
    
    Args:
        csv_file_path: Path to the geocoded CSV file
        output_file_path: Path to output CSV with found addresses
    """
    if not os.path.exists(csv_file_path):
        raise FileNotFoundError(f"CSV file not found: {csv_file_path}")
    
    if output_file_path is None:
        name, ext = os.path.splitext(csv_file_path)
        output_file_path = f"{name}_with_addresses{ext}"
    
    # Read the geocoded CSV
    with open(csv_file_path, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)
    
    print(f"Processing {len(rows)} rows...")
    
    # Find agencies without coordinates
    no_coords = [row for row in rows if not row.get('LATITUDE') or not row.get('LONGITUDE') or row['LATITUDE'] == '' or row['LONGITUDE'] == '']
    
    print(f"Found {len(no_coords)} agencies without coordinates")
    
    # Add ADDRESS_FOUND column if it doesn't exist
    fieldnames = reader.fieldnames
    if 'ADDRESS_FOUND' not in fieldnames:
        fieldnames = list(fieldnames) + ['ADDRESS_FOUND']
    
    # Process agencies without coordinates
    processed_count = 0
    found_count = 0
    
    for i, row in enumerate(no_coords):
        state = row.get('STATE', '').strip()
        agency = row.get('LAW ENFORCEMENT AGENCY', '').strip()
        county = row.get('COUNTY', '').strip()
        
        if not (state and agency):
            continue
        
        print(f"Processing {i+1}/{len(no_coords)}: {agency}, {state}")
        
        # Search for address
        found_address = search_web_for_address(agency, state)
        row['ADDRESS_FOUND'] = found_address
        
        if found_address:
            found_count += 1
            print(f"  Found address: {found_address}")
        else:
            print(f"  No address found")
        
        processed_count += 1
        
        # Add a delay to respect rate limits
        if (i + 1) % 5 == 0:
            time.sleep(1)
    
    # Write the updated CSV
    with open(output_file_path, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"Processed {processed_count} agencies, found addresses for {found_count}")
    print(f"Output saved to {output_file_path}")


if __name__ == "__main__":
    # Configuration
    CSV_FILE_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
        'participatingAgencies09042025pm_geocoded.csv'
    )
    OUTPUT_FILE_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
        'participatingAgencies09042025pm_missing_with_addresses.csv'
    )
    
    try:
        find_addresses_for_missing_agencies(CSV_FILE_PATH, OUTPUT_FILE_PATH)
        print("Address search completed successfully.")
    except Exception as e:
        print(f"Error during address search: {e}")
        import traceback
        traceback.print_exc()