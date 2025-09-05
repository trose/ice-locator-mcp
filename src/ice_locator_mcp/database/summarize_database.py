"""
Script to summarize the current state of the database.
"""
import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ice_locator_mcp.database.manager import DatabaseManager


def summarize_database(database_url: str):
    """
    Summarize the current state of the database.
    
    Args:
        database_url: PostgreSQL connection string
    """
    # Initialize database manager
    db_manager = DatabaseManager(database_url)
    db_manager.connect()
    
    try:
        # Get all facilities
        all_facilities = db_manager.get_all_facilities()
        
        # Get facilities without coordinates
        facilities_without_coords = db_manager.get_facilities_without_coordinates()
        
        # Get heatmap data
        heatmap_data = db_manager.get_heatmap_data()
        
        print("=== DATABASE SUMMARY ===")
        print(f"Total facilities: {len(all_facilities)}")
        print(f"Facilities without coordinates: {len(facilities_without_coords)}")
        print(f"Facilities with heatmap data: {len(heatmap_data)}")
        
        # Count facilities with valid coordinates
        facilities_with_coords = [f for f in all_facilities if f.latitude != 0.0 or f.longitude != 0.0]
        print(f"Facilities with valid coordinates: {len(facilities_with_coords)}")
        
        # Show some statistics
        if facilities_with_coords:
            print("\n=== COORDINATE STATISTICS ===")
            latitudes = [f.latitude for f in facilities_with_coords if f.latitude != 0.0]
            longitudes = [f.longitude for f in facilities_with_coords if f.longitude != 0.0]
            
            if latitudes:
                print(f"Latitude range: {min(latitudes):.6f} to {max(latitudes):.6f}")
            if longitudes:
                print(f"Longitude range: {min(longitudes):.6f} to {max(longitudes):.6f}")
        
        # Show top facilities by detainee count
        print("\n=== TOP FACILITIES BY DETAINEE COUNT ===")
        sorted_heatmap = sorted(heatmap_data, key=lambda x: x['detainee_count'], reverse=True)
        for i, facility in enumerate(sorted_heatmap[:10]):
            print(f"{i+1}. {facility['name']}: {facility['detainee_count']} detainees")
        
    finally:
        db_manager.disconnect()


if __name__ == "__main__":
    # Configuration
    DATABASE_URL = "postgresql://localhost/ice_locator"
    
    try:
        summarize_database(DATABASE_URL)
        print("\nDatabase summary completed successfully.")
    except Exception as e:
        print(f"Error during database summary: {e}")
        import traceback
        traceback.print_exc()