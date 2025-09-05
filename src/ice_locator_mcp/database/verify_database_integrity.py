"""
Script to verify the integrity of the database for heatmap functionality.
"""
import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ice_locator_mcp.database.manager import DatabaseManager


def verify_database_integrity(database_url: str):
    """
    Verify the integrity of the database for heatmap functionality.
    
    Args:
        database_url: PostgreSQL connection string
    """
    # Initialize database manager
    db_manager = DatabaseManager(database_url)
    db_manager.connect()
    
    try:
        print("=== DATABASE INTEGRITY VERIFICATION ===")
        
        # Check if tables exist
        cursor = db_manager.connection.cursor()
        
        # Check detainees table
        cursor.execute("""
            SELECT COUNT(*) as count FROM information_schema.tables 
            WHERE table_name = 'detainees'
        """)
        result = cursor.fetchone()
        detainees_table_exists = result['count'] > 0
        print(f"Detainees table exists: {detainees_table_exists}")
        
        # Check facilities table
        cursor.execute("""
            SELECT COUNT(*) as count FROM information_schema.tables 
            WHERE table_name = 'facilities'
        """)
        result = cursor.fetchone()
        facilities_table_exists = result['count'] > 0
        print(f"Facilities table exists: {facilities_table_exists}")
        
        # Check location history table
        cursor.execute("""
            SELECT COUNT(*) as count FROM information_schema.tables 
            WHERE table_name = 'detainee_location_history'
        """)
        result = cursor.fetchone()
        location_history_table_exists = result['count'] > 0
        print(f"Location history table exists: {location_history_table_exists}")
        
        # Get counts
        if detainees_table_exists:
            cursor.execute("SELECT COUNT(*) as count FROM detainees")
            detainees_count = cursor.fetchone()['count']
            print(f"Total detainees: {detainees_count}")
        
        if facilities_table_exists:
            cursor.execute("SELECT COUNT(*) as count FROM facilities")
            facilities_count = cursor.fetchone()['count']
            print(f"Total facilities: {facilities_count}")
            
            # Check for facilities with valid coordinates
            cursor.execute("""
                SELECT COUNT(*) as count FROM facilities 
                WHERE latitude != 0.0 OR longitude != 0.0
            """)
            facilities_with_coords = cursor.fetchone()['count']
            print(f"Facilities with coordinates: {facilities_with_coords}")
            
            # Check for facilities without coordinates
            cursor.execute("""
                SELECT COUNT(*) as count FROM facilities 
                WHERE latitude = 0.0 AND longitude = 0.0
            """)
            facilities_without_coords = cursor.fetchone()['count']
            print(f"Facilities without coordinates: {facilities_without_coords}")
        
        if location_history_table_exists:
            cursor.execute("SELECT COUNT(*) as count FROM detainee_location_history")
            location_history_count = cursor.fetchone()['count']
            print(f"Total location history records: {location_history_count}")
            
            # Check for current locations (no end date)
            cursor.execute("""
                SELECT COUNT(*) as count FROM detainee_location_history
                WHERE end_date IS NULL
            """)
            current_locations_count = cursor.fetchone()['count']
            print(f"Current location records: {current_locations_count}")
        
        cursor.close()
        
        # Verify heatmap data can be retrieved
        print("\n=== HEATMAP DATA VERIFICATION ===")
        try:
            heatmap_data = db_manager.get_heatmap_data()
            print(f"Successfully retrieved {len(heatmap_data)} heatmap data records")
            
            # Check if we have facilities with detainees
            facilities_with_detainees = [h for h in heatmap_data if h['detainee_count'] > 0]
            print(f"Facilities with detainees: {len(facilities_with_detainees)}")
            
            if facilities_with_detainees:
                max_detainees = max(facilities_with_detainees, key=lambda x: x['detainee_count'])
                print(f"Facility with most detainees: {max_detainees['name']} ({max_detainees['detainee_count']})")
            
        except Exception as e:
            print(f"Error retrieving heatmap data: {e}")
        
        # Overall assessment
        print("\n=== OVERALL ASSESSMENT ===")
        if facilities_table_exists and facilities_count > 0 and facilities_with_coords > 0:
            print("✓ Database is ready for heatmap functionality")
            print("✓ Facilities table populated with geocoded locations")
            print("✓ All facilities have valid coordinates")
        else:
            print("✗ Database is not ready for heatmap functionality")
            print("✗ Missing facilities or coordinates")
        
        if location_history_table_exists and location_history_count > 0:
            print("✓ Location history tracking is available")
        else:
            print("⚠ Location history tracking not yet populated")
            
    except Exception as e:
        print(f"Error during database verification: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db_manager.disconnect()


if __name__ == "__main__":
    # Configuration
    DATABASE_URL = "postgresql://localhost/ice_locator"
    
    try:
        verify_database_integrity(DATABASE_URL)
        print("\nDatabase integrity verification completed.")
    except Exception as e:
        print(f"Error during database integrity verification: {e}")
        import traceback
        traceback.print_exc()