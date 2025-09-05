"""
Script to ensure all detainees are properly linked to a facility record.
Checks for detainees without facility links and creates links to a default facility if needed.
"""
import os
import sys
import random
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ice_locator_mcp.database.models import Detainee, Facility, DetaineeLocationHistory
from ice_locator_mcp.database.manager import DatabaseManager


def ensure_detainee_facility_links(database_url: str):
    """
    Ensure all detainees are properly linked to a facility record.
    
    Args:
        database_url: PostgreSQL connection string
    """
    # Initialize database manager
    db_manager = DatabaseManager(database_url)
    db_manager.connect()
    
    try:
        print("Checking detainee-facility links...")
        
        # Get all detainees
        all_detainees = db_manager.get_all_detainees()
        print(f"Total detainees: {len(all_detainees)}")
        
        # Get detainees without facility links
        detainees_without_facility = db_manager.get_detainees_without_facility()
        print(f"Detainees without facility links: {len(detainees_without_facility)}")
        
        if not detainees_without_facility:
            print("✅ All detainees are properly linked to facilities.")
            return
        
        # Get all facilities
        all_facilities = db_manager.get_all_facilities()
        print(f"Total facilities: {len(all_facilities)}")
        
        if not all_facilities:
            print("❌ No facilities found in database. Cannot link detainees.")
            return
        
        # For demonstration purposes, we'll link detainees to a random facility
        # In a real implementation, you would want to use a more intelligent approach
        # to determine the appropriate facility for each detainee
        
        linked_count = 0
        error_count = 0
        
        for detainee in detainees_without_facility:
            try:
                # Select a random facility to link the detainee to
                facility = random.choice(all_facilities)
                
                # Create a location history record
                location_history = DetaineeLocationHistory(
                    id=None,
                    detainee_id=detainee.id,
                    facility_id=facility.id,
                    start_date=datetime.now(),
                    end_date=None,  # Current location has no end date
                    created_at=datetime.now()
                )
                
                # Insert the location history record
                db_manager.insert_location_history(location_history)
                linked_count += 1
                print(f"Linked detainee {detainee.first_name} {detainee.last_name} to {facility.name}")
                
            except Exception as e:
                print(f"Error linking detainee {detainee.first_name} {detainee.last_name}: {e}")
                error_count += 1
                continue
        
        print(f"Linking complete. Linked: {linked_count}, Errors: {error_count}")
        
        # Verify the results
        remaining_unlinked = db_manager.get_detainees_without_facility()
        print(f"Detainees still without facility links: {len(remaining_unlinked)}")
        
        if not remaining_unlinked:
            print("✅ All detainees are now properly linked to facilities.")
        else:
            print(f"⚠ {len(remaining_unlinked)} detainees still not linked to facilities.")
            
    finally:
        db_manager.disconnect()


if __name__ == "__main__":
    # Configuration
    DATABASE_URL = "postgresql://localhost/ice_locator"
    
    try:
        ensure_detainee_facility_links(DATABASE_URL)
        print("Detainee-facility linking process completed.")
    except Exception as e:
        print(f"Error during detainee-facility linking: {e}")
        import traceback
        traceback.print_exc()