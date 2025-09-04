"""
Script to update detainee locations daily.
This script would typically run as a cron job to query the MCP for facility updates
and store new data in the database.
"""
import random
from datetime import datetime
from .manager import DatabaseManager
from .models import DetaineeLocationHistory


def update_detainee_locations(database_url: str):
    """
    Update detainee locations by querying the MCP for facility updates.
    
    Args:
        database_url: PostgreSQL connection string
    """
    # Initialize database manager
    db_manager = DatabaseManager(database_url)
    db_manager.connect()
    
    try:
        print("Starting daily detainee location update...")
        
        # In a real implementation, this would query the MCP server for updates
        # For demonstration purposes, we'll simulate some updates
        
        # Get all facilities
        facilities = db_manager.get_all_facilities()
        
        if not facilities:
            print("No facilities found in database.")
            return
        
        # Get current location history to determine who might be transferred
        # This is a simplified approach - in reality, you'd query the MCP for actual updates
        
        # For demonstration, let's simulate a few transfers
        transfer_count = 0
        
        # Randomly select some detainees to transfer
        for _ in range(random.randint(1, 5)):
            # End a current location (simulate transfer out)
            current_locations = db_manager.get_current_detainee_count_by_facility()
            
            if current_locations:
                # Select a random facility with detainees
                facility_with_detainees = [f for f in current_locations if f['detainee_count'] > 0]
                
                if facility_with_detainees:
                    selected_facility = random.choice(facility_with_detainees)
                    
                    # In a real implementation, you would:
                    # 1. Query the MCP to get actual transfer information
                    # 2. End the current location history record
                    # 3. Create a new location history record for the new facility
                    
                    print(f"Simulated transfer from facility {selected_facility['facility_name']}")
                    transfer_count += 1
        
        # Add new detainees to facilities
        new_detainee_count = 0
        for _ in range(random.randint(2, 8)):
            facility = random.choice(facilities)
            
            # Create new location history record
            location_history = DetaineeLocationHistory(
                id=None,
                detainee_id=random.randint(1000, 2000),  # New detainee ID
                facility_id=facility.id,
                start_date=datetime.now(),
                end_date=None,  # Current location
                created_at=datetime.now()
            )
            
            try:
                db_manager.insert_location_history(location_history)
                new_detainee_count += 1
            except Exception as e:
                print(f"Error inserting new location history: {e}")
                continue
        
        print(f"Daily update completed: {transfer_count} transfers, {new_detainee_count} new detainees")
        
    finally:
        db_manager.disconnect()


def main():
    """Main function to run the daily update."""
    # This would normally be configured through environment variables
    DATABASE_URL = "postgresql://localhost/ice_locator"
    
    try:
        update_detainee_locations(DATABASE_URL)
        print("Detainee location update completed successfully.")
    except Exception as e:
        print(f"Error during detainee location update: {e}")


if __name__ == "__main__":
    main()