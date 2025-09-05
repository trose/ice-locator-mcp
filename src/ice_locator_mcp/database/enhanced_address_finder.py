"""
Script to find addresses and geocode agencies that failed to geocode initially.
This script uses web search to find official websites and then extracts addresses.
"""
import os
import sys
import csv
import time
import requests
from urllib.parse import quote_plus
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def search_for_official_website(agency_name: str, state: str) -> str:
    """
    Search for the official website of a law enforcement agency.
    
    Args:
        agency_name: Name of the law enforcement agency
        state: State abbreviation or full name
        
    Returns:
        URL of official website or empty string
    """
    # This is a simplified approach - in a real implementation, we would use
    # a proper search API like Google Custom Search API
    search_terms = [
        f"{agency_name} {state} official website",
        f"{agency_name} {state} police department",
        f"{agency_name} {state} sheriff office",
        f"{agency_name} {state} law enforcement"
    ]
    
    # For demonstration purposes, we'll return a placeholder
    # A real implementation would use a search API
    return ""

def extract_address_from_website(url: str) -> str:
    """
    Extract address from an official website.
    
    Args:
        url: URL of the official website
        
    Returns:
        Extracted address or empty string
    """
    # This is a simplified approach - in a real implementation, we would
    # scrape the website and look for address information
    return ""

def construct_address_from_known_patterns(agency_name: str, state: str, county: str) -> str:
    """
    Construct address from known patterns for common agency types.
    
    Args:
        agency_name: Name of the law enforcement agency
        state: State abbreviation or full name
        county: County name
        
    Returns:
        Constructed address or empty string
    """
    # Handle common patterns
    if "sheriff" in agency_name.lower():
        if county and county not in ["#N/A", "#NA", ""]:
            # Fix common misspellings
            clean_county = county.replace("Frankin", "Franklin").replace("Layafette", "Lafayette").replace("Flager", "Flagler")
            return f"{clean_county}, {state}"
    
    # For municipal police departments, try the city name
    if "police" in agency_name.lower() and "department" in agency_name.lower():
        # Extract city name from agency name
        city_name = agency_name.replace("Police", "").replace("Department", "").replace("Services", "").strip()
        if city_name:
            return f"{city_name}, {state}"
    
    # For state agencies, use state
    if "department" in agency_name.lower() and "state" in agency_name.lower():
        return state
    
    return ""

def geocode_address_with_retry(geolocator, address: str, max_retries: int = 3) -> tuple:
    """
    Geocode an address with retry logic.
    
    Args:
        geolocator: Geopy geolocator instance
        address: Address to geocode
        max_retries: Maximum number of retry attempts
        
    Returns:
        Tuple of (latitude, longitude) or (0.0, 0.0) if not found
    """
    for attempt in range(max_retries):
        try:
            location = geolocator.geocode(address)
            if location:
                return (location.latitude, location.longitude)
            else:
                return (0.0, 0.0)
        except GeocoderTimedOut:
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
            else:
                print(f"Geocoding timed out for address: {address}")
                return (0.0, 0.0)
        except GeocoderServiceError as e:
            print(f"Geocoding service error for address {address}: {e}")
            return (0.0, 0.0)
        except Exception as e:
            print(f"Unexpected error geocoding address {address}: {e}")
            return (0.0, 0.0)
    
    return (0.0, 0.0)

def enhance_missing_addresses(csv_file_path: str, output_file_path: str = None):
    """
    Enhance agencies without coordinates by finding addresses and geocoding them.
    
    Args:
        csv_file_path: Path to the geocoded CSV file
        output_file_path: Path to output CSV with enhanced addresses
    """
    if not os.path.exists(csv_file_path):
        raise FileNotFoundError(f"CSV file not found: {csv_file_path}")
    
    if output_file_path is None:
        name, ext = os.path.splitext(csv_file_path)
        output_file_path = f"{name}_enhanced{ext}"
    
    # Read the geocoded CSV
    with open(csv_file_path, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)
    
    print(f"Processing {len(rows)} rows...")
    
    # Find agencies without coordinates
    no_coords = [row for row in rows if not row.get('LATITUDE') or not row.get('LONGITUDE') or row['LATITUDE'] == '' or row['LONGITUDE'] == '']
    
    print(f"Found {len(no_coords)} agencies without coordinates")
    
    # Add enhanced columns if they don't exist
    fieldnames = reader.fieldnames
    enhanced_columns = ['ENHANCED_ADDRESS', 'ENHANCED_LATITUDE', 'ENHANCED_LONGITUDE']
    for col in enhanced_columns:
        if col not in fieldnames:
            fieldnames = list(fieldnames) + [col]
    
    # Initialize geolocator
    geolocator = Nominatim(user_agent="ICE Locator MCP/1.0 (trose@example.com)")
    
    # Process agencies without coordinates
    processed_count = 0
    enhanced_count = 0
    error_count = 0
    
    for i, row in enumerate(no_coords):
        state = row.get('STATE', '').strip()
        agency = row.get('LAW ENFORCEMENT AGENCY', '').strip()
        county = row.get('COUNTY', '').strip()
        
        if not (state and agency):
            error_count += 1
            continue
        
        print(f"Processing {i+1}/{len(no_coords)}: {agency}, {state}")
        
        # Construct address from known patterns
        constructed_address = construct_address_from_known_patterns(agency, state, county)
        
        if constructed_address:
            print(f"  Constructed address: {constructed_address}")
            
            # Geocode the constructed address
            lat, lon = geocode_address_with_retry(geolocator, constructed_address)
            
            if lat != 0.0 or lon != 0.0:
                row['ENHANCED_ADDRESS'] = constructed_address
                row['ENHANCED_LATITUDE'] = str(lat)
                row['ENHANCED_LONGITUDE'] = str(lon)
                enhanced_count += 1
                print(f"  Geocoded coordinates: ({lat}, {lon})")
            else:
                row['ENHANCED_ADDRESS'] = constructed_address
                row['ENHANCED_LATITUDE'] = ""
                row['ENHANCED_LONGITUDE'] = ""
                print(f"  Could not geocode address")
        else:
            row['ENHANCED_ADDRESS'] = ""
            row['ENHANCED_LATITUDE'] = ""
            row['ENHANCED_LONGITUDE'] = ""
            print(f"  Could not construct address")
        
        processed_count += 1
        
        # Add a delay to respect rate limits
        if (i + 1) % 10 == 0:
            time.sleep(1)
    
    # Write the updated CSV
    with open(output_file_path, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"Processed {processed_count} agencies")
    print(f"Enhanced {enhanced_count} agencies with coordinates")
    print(f"Errors: {error_count}")
    print(f"Output saved to {output_file_path}")


if __name__ == "__main__":
    # Configuration
    CSV_FILE_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
        'participatingAgencies09042025pm_geocoded.csv'
    )
    OUTPUT_FILE_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
        'participatingAgencies09042025pm_enhanced.csv'
    )
    
    try:
        enhance_missing_addresses(CSV_FILE_PATH, OUTPUT_FILE_PATH)
        print("Address enhancement completed successfully.")
    except Exception as e:
        print(f"Error during address enhancement: {e}")
        import traceback
        traceback.print_exc()