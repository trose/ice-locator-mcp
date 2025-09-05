"""
Script to process facilities in the database that don't have lat/long coordinates.
This script will attempt to geocode facilities that are missing coordinates.
"""
import os
import sys
import time
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ice_locator_mcp.database.models import Facility
from ice_locator_mcp.database.manager import DatabaseManager


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


def process_facilities_without_coordinates(database_url: str):
    """
    Process facilities in the database that don't have lat/long coordinates.
    
    Args:
        database_url: PostgreSQL connection string
    """
    # Initialize database manager
    db_manager = DatabaseManager(database_url)
    db_manager.connect()
    
    try:
        # Get facilities without coordinates
        facilities_without_coords = db_manager.get_facilities_without_coordinates()
        
        if not facilities_without_coords:
            print("No facilities found without coordinates.")
            return
        
        print(f"Found {len(facilities_without_coords)} facilities without coordinates.")
        
        # Initialize geolocator
        geolocator = Nominatim(user_agent="ICE Locator MCP/1.0 (trose@example.com)")
        
        updated_count = 0
        error_count = 0
        
        for i, facility in enumerate(facilities_without_coords):
            print(f"Processing {i+1}/{len(facilities_without_coords)}: {facility.name}")
            
            # Try to geocode the facility name as an address
            lat, lon = geocode_address_with_retry(geolocator, facility.name)
            
            if lat != 0.0 or lon != 0.0:
                # Update the facility with new coordinates
                cursor = db_manager.connection.cursor()
                cursor.execute("""
                    UPDATE facilities 
                    SET latitude = %s, longitude = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (lat, lon, facility.id))
                
                db_manager.connection.commit()
                cursor.close()
                
                print(f"  Updated coordinates for {facility.name}: ({lat}, {lon})")
                updated_count += 1
            else:
                print(f"  Could not geocode coordinates for {facility.name}")
                error_count += 1
            
            # Add a delay to respect API rate limits
            if (i + 1) % 10 == 0:
                time.sleep(1)
        
        print(f"Processing complete. Updated: {updated_count}, Errors: {error_count}")
        
    finally:
        db_manager.disconnect()


if __name__ == "__main__":
    # Configuration
    DATABASE_URL = "postgresql://localhost/ice_locator"
    
    try:
        process_facilities_without_coordinates(DATABASE_URL)
        print("Facility coordinate processing completed successfully.")
    except Exception as e:
        print(f"Error during facility coordinate processing: {e}")
        import traceback
        traceback.print_exc()