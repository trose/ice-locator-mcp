"""
Script to ingest participating agencies from CSV and lookup GPS coordinates.
Uses multiple geocoding services with fallback options.
"""
import os
import csv
import requests
import time
from datetime import datetime
from .models import Facility
from .manager import DatabaseManager


def get_unique_facilities_from_csv(csv_file_path: str) -> list:
    """
    Extract unique facility names from the participating agencies CSV.
    
    Args:
        csv_file_path: Path to the CSV file
        
    Returns:
        List of unique facility names
    """
    if not os.path.exists(csv_file_path):
        raise FileNotFoundError(f"CSV file not found: {csv_file_path}")
    
    facilities = set()
    
    # Read facilities from CSV
    with open(csv_file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Combine state and law enforcement agency to create unique facility names
            state = row.get('STATE', '').strip()
            agency = row.get('LAW ENFORCEMENT AGENCY', '').strip()
            
            if state and agency:
                facility_name = f"{agency}, {state}"
                facilities.add(facility_name)
    
    return list(facilities)


def geocode_facility_nominatim(facility_name: str) -> tuple:
    """
    Lookup GPS coordinates for a facility using Nominatim (OpenStreetMap) geocoding service.
    
    Args:
        facility_name: Name of the facility to geocode
        
    Returns:
        Tuple of (latitude, longitude) or (0.0, 0.0) if not found
    """
    try:
        # Use Nominatim geocoding service (no API key required)
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': facility_name,
            'format': 'json',
            'limit': 1
        }
        headers = {
            'User-Agent': 'ICE Locator MCP/1.0 (trose@example.com)'  # Required by Nominatim ToS
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        results = response.json()
        if results and len(results) > 0:
            location = results[0]
            return (float(location['lat']), float(location['lon']))
        else:
            print(f"Warning: No geocode result for {facility_name}")
            return (0.0, 0.0)
    except Exception as e:
        print(f"Error geocoding {facility_name} with Nominatim: {e}")
        return (0.0, 0.0)


def geocode_facility_google(facility_name: str, google_api_key: str) -> tuple:
    """
    Lookup GPS coordinates for a facility using Google Maps Geocoding API.
    
    Args:
        facility_name: Name of the facility to geocode
        google_api_key: Google Maps API key
        
    Returns:
        Tuple of (latitude, longitude) or (0.0, 0.0) if not found
    """
    try:
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            'address': facility_name,
            'key': google_api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        if result['status'] == 'OK' and len(result['results']) > 0:
            location = result['results'][0]['geometry']['location']
            return (location['lat'], location['lng'])
        else:
            print(f"Warning: Google geocode failed for {facility_name} - {result['status']}")
            return (0.0, 0.0)
    except Exception as e:
        print(f"Error geocoding {facility_name} with Google: {e}")
        return (0.0, 0.0)


def geocode_facility(facility_name: str, google_api_key: str = None) -> tuple:
    """
    Lookup GPS coordinates for a facility using multiple geocoding services.
    
    Args:
        facility_name: Name of the facility to geocode
        google_api_key: Google Maps API key (optional)
        
    Returns:
        Tuple of (latitude, longitude) or (0.0, 0.0) if not found
    """
    # Try Nominatim first (no API key required)
    lat, lon = geocode_facility_nominatim(facility_name)
    if lat != 0.0 and lon != 0.0:
        return (lat, lon)
    
    # Fallback to Google Maps if API key is provided
    if google_api_key:
        lat, lon = geocode_facility_google(facility_name, google_api_key)
        if lat != 0.0 and lon != 0.0:
            return (lat, lon)
    
    # If all methods fail, return default coordinates
    return (0.0, 0.0)


def ingest_participating_agencies(database_url: str, csv_file_path: str = None, google_api_key: str = None):
    """
    Ingest participating agencies from CSV, deduplicate, geocode, and store in database.
    
    Args:
        database_url: PostgreSQL connection string
        csv_file_path: Path to the CSV file
        google_api_key: Google Maps API key (optional)
    """
    if csv_file_path is None:
        csv_file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            'participatingAgencies09042025pm.csv'
        )
    
    if not google_api_key:
        google_api_key = os.environ.get('GOOGLE_API_KEY')
    
    # Initialize database manager
    db_manager = DatabaseManager(database_url)
    db_manager.connect()
    
    try:
        # Get unique facility list
        facilities = get_unique_facilities_from_csv(csv_file_path)
        print(f"Found {len(facilities)} unique facilities in CSV")
        
        processed_count = 0
        skipped_count = 0
        error_count = 0
        geocoded_count = 0
        
        for i, facility_name in enumerate(facilities):
            # Check if facility already exists (using the unique constraint)
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
            
            # Geocode the facility
            print(f"Geocoding facility {i+1}/{len(facilities)}: {facility_name}")
            lat, lon = geocode_facility(facility_name, google_api_key)
            
            if lat != 0.0 or lon != 0.0:
                geocoded_count += 1
            
            # Create facility object
            facility = Facility(
                id=None,
                name=facility_name,
                latitude=lat,
                longitude=lon,
                address=None,
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
            if (i + 1) % 5 == 0:
                time.sleep(1)
        
        print(f"Ingestion complete. Processed: {processed_count}, Skipped: {skipped_count}, Errors: {error_count}, Geocoded: {geocoded_count}")
        
    finally:
        db_manager.disconnect()


if __name__ == "__main__":
    # Configuration
    DATABASE_URL = "postgresql://localhost/ice_locator"
    CSV_FILE_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
        'participatingAgencies09042025pm.csv'
    )
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    
    try:
        ingest_participating_agencies(DATABASE_URL, CSV_FILE_PATH, GOOGLE_API_KEY)
        print("Facility ingestion completed successfully.")
    except Exception as e:
        print(f"Error during facility ingestion: {e}")
        import traceback
        traceback.print_exc()