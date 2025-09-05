"""
Script to enrich participating agencies CSV with plausible addresses and geocode them.
Uses county information to construct addresses and geocodes them using geopy.
"""
import os
import csv
import time
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError


def construct_search_address(agency_name: str, county: str, state: str) -> str:
    """
    Construct a search address for geocoding.
    
    Args:
        agency_name: Name of the law enforcement agency
        county: County name
        state: State abbreviation or full name
        
    Returns:
        Search address string
    """
    # For sheriff's offices, search for the county
    if "sheriff" in agency_name.lower() and "county" in county.lower():
        # Remove "County" from county name if it's already there
        clean_county = county.replace("County", "").strip()
        return f"{clean_county} County, {state}"
    else:
        # For other agencies, search for the agency in the county
        return f"{agency_name}, {county}, {state}"


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


def enrich_csv_with_geocoded_addresses(csv_file_path: str, output_file_path: str = None):
    """
    Enrich the CSV with geocoded addresses for each agency.
    
    Args:
        csv_file_path: Path to the input CSV file
        output_file_path: Path to the output CSV file (defaults to input file with _geocoded suffix)
    """
    if not os.path.exists(csv_file_path):
        raise FileNotFoundError(f"CSV file not found: {csv_file_path}")
    
    if output_file_path is None:
        name, ext = os.path.splitext(csv_file_path)
        output_file_path = f"{name}_geocoded{ext}"
    
    # Initialize geolocator
    geolocator = Nominatim(user_agent="ICE Locator MCP/1.0 (trose@example.com)")
    
    # Read the original CSV
    with open(csv_file_path, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)
    
    print(f"Processing {len(rows)} rows...")
    
    # Add ADDRESS, LATITUDE, and LONGITUDE columns if they don't exist
    fieldnames = reader.fieldnames
    if 'ADDRESS' not in fieldnames:
        fieldnames = list(fieldnames) + ['ADDRESS']
    if 'LATITUDE' not in fieldnames:
        fieldnames = list(fieldnames) + ['LATITUDE']
    if 'LONGITUDE' not in fieldnames:
        fieldnames = list(fieldnames) + ['LONGITUDE']
    
    # Process ALL rows
    enriched_rows = []
    geocoded_count = 0
    error_count = 0
    
    # Check if output file already exists and has processed rows
    processed_rows = 0
    if os.path.exists(output_file_path):
        with open(output_file_path, 'r', encoding='utf-8') as existing_file:
            existing_reader = csv.DictReader(existing_file)
            existing_rows = list(existing_reader)
            processed_rows = len(existing_rows) - 1  # Subtract header row
            if processed_rows > 0:
                print(f"Resuming from row {processed_rows + 1}")
                enriched_rows = existing_rows[1:]  # Skip header
    
    for i in range(processed_rows, len(rows)):
        row = rows[i]
        state = row.get('STATE', '').strip()
        agency = row.get('LAW ENFORCEMENT AGENCY', '').strip()
        county = row.get('COUNTY', '').strip()
        
        if state and agency and county:
            print(f"Processing {i+1}/{len(rows)}: {agency}, {county}, {state}")
            
            # Construct a search address
            search_address = construct_search_address(agency, county, state)
            print(f"  Search address: {search_address}")
            
            # Geocode the address
            lat, lon = geocode_address_with_retry(geolocator, search_address)
            
            # Add address and coordinates to row
            row['ADDRESS'] = search_address
            row['LATITUDE'] = str(lat) if lat != 0.0 else ""
            row['LONGITUDE'] = str(lon) if lon != 0.0 else ""
            
            if lat != 0.0 or lon != 0.0:
                print(f"  Geocoded coordinates: ({lat}, {lon})")
                geocoded_count += 1
            else:
                print(f"  No coordinates found")
                error_count += 1
        else:
            row['ADDRESS'] = ""
            row['LATITUDE'] = ""
            row['LONGITUDE'] = ""
            error_count += 1
        
        enriched_rows.append(row)
        
        # Write batch of rows to file every 50 rows
        if (i + 1) % 50 == 0 or i == len(rows) - 1:
            # Write the enriched CSV
            with open(output_file_path, 'w', newline='', encoding='utf-8') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(enriched_rows)
            print(f"  Saved progress to {output_file_path}")
        
        # Add a delay to respect API rate limits
        if (i + 1) % 10 == 0:
            time.sleep(1)
    
    # Write the final enriched CSV
    with open(output_file_path, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(enriched_rows)
    
    print(f"Geocoded CSV saved to {output_file_path}")
    print(f"Processed {len(rows)} rows, successfully geocoded {geocoded_count} rows, errors: {error_count}")


if __name__ == "__main__":
    # Configuration
    CSV_FILE_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
        'participatingAgencies09042025pm.csv'
    )
    OUTPUT_FILE_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
        'participatingAgencies09042025pm_geocoded.csv'
    )
    
    try:
        enrich_csv_with_geocoded_addresses(CSV_FILE_PATH, OUTPUT_FILE_PATH)
        print("CSV geocoding completed successfully.")
    except Exception as e:
        print(f"Error during CSV geocoding: {e}")
        import traceback
        traceback.print_exc()