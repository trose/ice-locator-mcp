"""
Script to populate location history for detainees based on real CSV data.
This script properly matches detainees to facilities based on the enriched_detainees.csv data.
"""
import csv
import os
import sys
from datetime import datetime, timedelta
from .models import DetaineeLocationHistory
from .manager import DatabaseManager


def populate_real_location_history(database_url: str, csv_file_path: str = None):
    """
    Populate location history for detainees based on real CSV data.
    
    Args:
        database_url: PostgreSQL connection string
        csv_file_path: Path to the CSV file
    """
    if csv_file_path is None:
        csv_file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            'enriched_detainees.csv'
        )
    
    if not os.path.exists(csv_file_path):
        raise FileNotFoundError(f"CSV file not found: {csv_file_path}")
    
    # Initialize database manager
    db_manager = DatabaseManager(database_url)
    db_manager.connect()
    
    try:
        # Get all facilities
        facilities = db_manager.get_all_facilities()
        
        if not facilities:
            print("No facilities found in database. Please run seed_facility_locations.py first.")
            return
        
        # Create a facility lookup dictionary for faster matching
        facility_lookup = {facility.name.lower(): facility for facility in facilities}
        
        # Get all detainees (we'll need to match them by name)
        # For this implementation, we'll recreate the matching logic
        
        location_history_count = 0
        
        # Read CSV and create location history for each detainee
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                # Extract relevant information
                facility_name = row.get('facility_name', '').strip()
                first_name = row.get('first_name', '').strip()
                last_name = row.get('last_name', '').strip()
                
                # Skip if no facility or name data
                if not facility_name or not first_name or not last_name:
                    continue
                
                # Find matching facility
                matching_facility = facility_lookup.get(facility_name.lower())
                
                # If no exact match, try partial matching or skip
                if not matching_facility:
                    # Try to find a facility that contains the name
                    for name, facility in facility_lookup.items():
                        if facility_name.lower() in name or name in facility_name.lower():
                            matching_facility = facility
                            break
                
                if not matching_facility:
                    print(f"Warning: No matching facility found for '{facility_name}', skipping...")
                    continue
                
                # Find the detainee by name (this is a simplified approach)
                # In a real implementation, you would have a better way to match detainees
                # For now, we'll just create a new location history record with a placeholder
                # In a production system, you would properly match detainees by ID or unique identifiers
                
                # Create location history object (current location with no end date)
                # We'll use a placeholder for detainee_id since we don't have a proper matching system
                # In a real implementation, you would properly match detainees
                
                location_history = DetaineeLocationHistory(
                    id=None,
                    detainee_id=location_history_count + 1,  # Placeholder - would match actual detainee ID
                    facility_id=matching_facility.id,
                    start_date=datetime.now() - timedelta(days=30),  # Assume they've been there for 30 days
                    end_date=None,  # Current location has no end date
                    created_at=datetime.now()
                )
                
                # Insert into database
                try:
                    db_manager.insert_location_history(location_history)
                    location_history_count += 1
                    
                    if location_history_count % 100 == 0:
                        print(f"Processed {location_history_count} location history records...")
                except Exception as e:
                    print(f"Error inserting location history for {first_name} {last_name}: {e}")
                    continue
        
        print(f"Successfully created {location_history_count} location history records")
        
    finally:
        db_manager.disconnect()


def populate_location_history_from_database(database_url: str):
    """
    Populate location history by properly matching detainees from the database.
    
    Args:
        database_url: PostgreSQL connection string
    """
    # Initialize database manager
    db_manager = DatabaseManager(database_url)
    db_manager.connect()
    
    try:
        # Get all facilities
        facilities = db_manager.get_all_facilities()
        
        if not facilities:
            print("No facilities found in database.")
            return
        
        # Create a facility lookup dictionary
        facility_lookup = {facility.name.lower(): facility for facility in facilities}
        
        # Get all detainees and create a lookup by name
        cursor = db_manager.connection.cursor()
        cursor.execute("SELECT id, first_name, last_name FROM detainees")
        detainees = cursor.fetchall()
        
        # Create a lookup dictionary for detainees by full name
        detainee_lookup = {}
        for detainee in detainees:
            full_name = f"{detainee['first_name']} {detainee['last_name']}".lower()
            detainee_lookup[full_name] = detainee['id']
        
        print(f"Loaded {len(detainee_lookup)} detainees from database")
        
        # Read CSV data to get facility assignments
        csv_file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            'enriched_detainees.csv'
        )
        
        if not os.path.exists(csv_file_path):
            raise FileNotFoundError(f"CSV file not found: {csv_file_path}")
        
        location_history_count = 0
        errors = 0
        
        # Read CSV and create location history for each detainee
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                # Extract relevant information
                facility_name = row.get('facility_name', '').strip()
                first_name = row.get('first_name', '').strip()
                last_name = row.get('last_name', '').strip()
                
                # Skip if no facility or name data
                if not facility_name or not first_name or not last_name:
                    continue
                
                # Find matching facility
                matching_facility = facility_lookup.get(facility_name.lower())
                
                if not matching_facility:
                    print(f"Warning: No matching facility found for '{facility_name}', skipping...")
                    errors += 1
                    continue
                
                # Find matching detainee
                full_name = f"{first_name} {last_name}".lower()
                detainee_id = detainee_lookup.get(full_name)
                
                if not detainee_id:
                    # Try partial matching
                    matched = False
                    for name, id in detainee_lookup.items():
                        if full_name in name or name in full_name:
                            detainee_id = id
                            matched = True
                            break
                    
                    if not matched:
                        print(f"Warning: No matching detainee found for '{full_name}', skipping...")
                        errors += 1
                        continue
                
                # Create location history object
                location_history = DetaineeLocationHistory(
                    id=None,
                    detainee_id=detainee_id,
                    facility_id=matching_facility.id,
                    start_date=datetime.now() - timedelta(days=30),
                    end_date=None,  # Current detainees
                    created_at=datetime.now()
                )
                
                # Insert into database
                try:
                    db_manager.insert_location_history(location_history)
                    location_history_count += 1
                    if location_history_count % 100 == 0:
                        print(f"Processed {location_history_count} location history records...")
                except Exception as e:
                    print(f"Error inserting location history for {first_name} {last_name}: {e}")
                    errors += 1
                    # Continue with next record
                    continue
        
        print(f"Successfully created {location_history_count} location history records from CSV data")
        if errors > 0:
            print(f"Encountered {errors} errors during processing")
        
    finally:
        db_manager.disconnect()


if __name__ == "__main__":
    # This would normally be configured through environment variables
    DATABASE_URL = "postgresql://localhost/ice_locator"
    
    # Populate location history from CSV data
    populate_location_history_from_database(DATABASE_URL)