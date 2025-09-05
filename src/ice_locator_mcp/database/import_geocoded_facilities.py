"""
Script to import geocoded facilities from CSV into the database.
Reads the geocoded CSV file and inserts facilities with their coordinates into the database.
"""
import os
import sys
import csv
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ice_locator_mcp.database.models import Facility
from ice_locator_mcp.database.manager import DatabaseManager


def import_geocoded_facilities(database_url: str, csv_file_path: str = None):
    """
    Import geocoded facilities from CSV into the database.
    
    Args:
        database_url: PostgreSQL connection string
        csv_file_path: Path to the geocoded CSV file
    """
    if csv_file_path is None:
        csv_file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            'participatingAgencies09042025pm_geocoded.csv'
        )
    
    if not os.path.exists(csv_file_path):
        raise FileNotFoundError(f"Geocoded CSV file not found: {csv_file_path}")
    
    # Initialize database manager
    db_manager = DatabaseManager(database_url)
    db_manager.connect()
    
    try:
        imported_count = 0
        skipped_count = 0
        error_count = 0
        duplicate_count = 0
        
        # Read the geocoded CSV
        with open(csv_file_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            rows = list(reader)
        
        print(f"Processing {len(rows)} facilities from geocoded CSV...")
        
        for i, row in enumerate(rows):
            state = row.get('STATE', '').strip()
            agency = row.get('LAW ENFORCEMENT AGENCY', '').strip()
            address = row.get('ADDRESS', '').strip()
            latitude = row.get('LATITUDE', '').strip()
            longitude = row.get('LONGITUDE', '').strip()
            
            if not (state and agency):
                print(f"Skipping row {i+1}: Missing state or agency")
                skipped_count += 1
                continue
            
            # Create facility name
            facility_name = f"{agency}, {state}"
            
            # Check if facility already exists
            try:
                existing_facilities = db_manager.get_all_facilities()
                if any(f.name == facility_name for f in existing_facilities):
                    print(f"Facility {facility_name} already exists, skipping...")
                    duplicate_count += 1
                    continue
            except Exception as e:
                print(f"Error checking existing facilities: {e}")
                error_count += 1
                continue
            
            # Parse coordinates
            try:
                lat = float(latitude) if latitude else 0.0
                lon = float(longitude) if longitude else 0.0
            except ValueError:
                lat, lon = 0.0, 0.0
            
            # Skip facilities without coordinates
            if lat == 0.0 and lon == 0.0:
                print(f"Skipping facility {facility_name}: No coordinates")
                skipped_count += 1
                continue
            
            # Create facility object
            facility = Facility(
                id=None,
                name=facility_name,
                latitude=lat,
                longitude=lon,
                address=address if address else None,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Insert into database
            try:
                db_manager.insert_facility(facility)
                imported_count += 1
                coord_info = f"({lat}, {lon})" if lat != 0.0 or lon != 0.0 else "(no coordinates)"
                print(f"Imported facility {imported_count}: {facility_name} {coord_info}")
            except Exception as e:
                print(f"Error inserting facility {facility_name}: {e}")
                error_count += 1
                continue
        
        print(f"Import complete. Imported: {imported_count}, Skipped: {skipped_count}, Duplicates: {duplicate_count}, Errors: {error_count}")
        
    finally:
        db_manager.disconnect()


if __name__ == "__main__":
    # Configuration
    DATABASE_URL = "postgresql://localhost/ice_locator"
    CSV_FILE_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
        'participatingAgencies09042025pm_geocoded.csv'
    )
    
    try:
        import_geocoded_facilities(DATABASE_URL, CSV_FILE_PATH)
        print("Facility import completed successfully.")
    except Exception as e:
        print(f"Error during facility import: {e}")
        import traceback
        traceback.print_exc()