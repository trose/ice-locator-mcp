"""
Script to geocode facility addresses using the geopy library.
This script demonstrates how to convert addresses to latitude/longitude coordinates.
"""
import os
import csv
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import time
from datetime import datetime
from .models import Facility
from .manager import DatabaseManager


def get_unique_agencies_from_csv(csv_file_path: str) -> list:
    """
    Extract unique law enforcement agencies from the participating agencies CSV.
    
    Args:
        csv_file_path: Path to the CSV file
        
    Returns:
        List of unique agency information
    """
    if not os.path.exists(csv_file_path):
        raise FileNotFoundError(f"CSV file not found: {csv_file_path}")
    
    agencies = {}
    
    # Read agencies from CSV
    with open(csv_file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            state = row.get('STATE', '').strip()
            agency = row.get('LAW ENFORCEMENT AGENCY', '').strip()
            county = row.get('COUNTY', '').strip()
            agency_type = row.get('TYPE', '').strip()
            
            if state and agency:
                # Create a unique key for deduplication
                key = f"{agency}|{state}"
                if key not in agencies:
                    agencies[key] = {
                        'agency': agency,
                        'state': state,
                        'county': county,
                        'type': agency_type
                    }
    
    return list(agencies.values())


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


def format_address_for_geocoding(agency_info: dict) -> str:
    """
    Format agency information into a geocodable address.
    
    Args:
        agency_info: Dictionary containing agency information
        
    Returns:
        Formatted address string
    """
    agency = agency_info['agency']
    county = agency_info['county']
    state = agency_info['state']
    
    # Create a search-friendly address
    if county:
        return f"{agency}, {county} County, {state}, USA"
    else:
        return f"{agency}, {state}, USA"


def geocode_facilities_from_csv(database_url: str, csv_file_path: str = None):
    """
    Geocode facilities from CSV and store in database.
    
    Args:
        database_url: PostgreSQL connection string
        csv_file_path: Path to the CSV file
    """
    if csv_file_path is None:
        csv_file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            'participatingAgencies09042025pm.csv'
        )
    
    # Initialize geolocator (Nominatim)
    geolocator = Nominatim(user_agent="ICE Locator MCP/1.0 (trose@example.com)")
    
    # Initialize database manager
    db_manager = DatabaseManager(database_url)
    db_manager.connect()
    
    try:
        # Get unique agencies
        agencies = get_unique_agencies_from_csv(csv_file_path)
        print(f"Found {len(agencies)} unique agencies in CSV")
        
        processed_count = 0
        skipped_count = 0
        error_count = 0
        geocoded_count = 0
        
        # Process first 10 agencies as a sample
        sample_agencies = agencies[:10]
        print(f"Processing first {len(sample_agencies)} agencies as sample...")
        
        for i, agency_info in enumerate(sample_agencies):
            agency_name = agency_info['agency']
            state = agency_info['state']
            facility_name = f"{agency_name}, {state}"
            
            # Check if facility already exists
            try:
                existing_facilities = db_manager.get_all_facilities()
                if any(f.name == facility_name for f in existing_facilities):
                    print(f"Facility {facility_name} already exists, skipping...")
                    skipped_count += 1
                    continue
            except Exception as e:
                print(f"Error checking existing facilities: {e}")
                error_count += 1
                continue
            
            # Format address for geocoding
            address = format_address_for_geocoding(agency_info)
            print(f"Geocoding agency {i+1}/{len(sample_agencies)}: {address}")
            
            # Geocode the address
            lat, lon = geocode_address_with_retry(geolocator, address)
            
            if lat != 0.0 or lon != 0.0:
                geocoded_count += 1
            
            # Create facility object
            facility = Facility(
                id=None,
                name=facility_name,
                latitude=lat,
                longitude=lon,
                address=address,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Insert into database
            try:
                db_manager.insert_facility(facility)
                processed_count += 1
                coord_info = f"({lat}, {lon})" if lat != 0.0 or lon != 0.0 else "(no coordinates)"
                print(f"Successfully ingested facility: {facility_name} {coord_info}")
            except Exception as e:
                print(f"Error inserting facility {facility_name}: {e}")
                error_count += 1
                continue
            
            # Add a small delay to respect API rate limits
            time.sleep(1)
        
        print(f"Sample processing complete. Processed: {processed_count}, Skipped: {skipped_count}, Errors: {error_count}, Geocoded: {geocoded_count}")
        
    finally:
        db_manager.disconnect()


if __name__ == "__main__":
    # Configuration
    DATABASE_URL = "postgresql://localhost/ice_locator"
    CSV_FILE_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
        'participatingAgencies09042025pm.csv'
    )
    
    try:
        geocode_facilities_from_csv(DATABASE_URL, CSV_FILE_PATH)
        print("Facility geocoding completed successfully.")
    except Exception as e:
        print(f"Error during facility geocoding: {e}")
        import traceback
        traceback.print_exc()