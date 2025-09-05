"""
Script to check facilities in the database that don't have lat/long coordinates.
"""
import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ice_locator_mcp.database.manager import DatabaseManager


def check_facilities_without_coordinates(database_url: str):
    """
    Check facilities in the database that don't have lat/long coordinates.
    
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
        
        print(f"Found {len(facilities_without_coords)} facilities without coordinates:")
        for facility in facilities_without_coords:
            print(f"  - {facility.name}")
        
    finally:
        db_manager.disconnect()


if __name__ == "__main__":
    # Configuration
    DATABASE_URL = "postgresql://localhost/ice_locator"
    
    try:
        check_facilities_without_coordinates(DATABASE_URL)
        print("Facility check completed successfully.")
    except Exception as e:
        print(f"Error during facility check: {e}")
        import traceback
        traceback.print_exc()