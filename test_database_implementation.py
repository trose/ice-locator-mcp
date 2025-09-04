"""
Simple test script to verify database implementation.
"""
import sys
import os

# Add the database directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'ice_locator_mcp'))

try:
    # Test importing the database models directly
    from database.models import Detainee, Facility, DetaineeLocationHistory
    print("Database models imported successfully")
    
    # Test model creation
    detainee = Detainee(
        id=None,
        first_name="John",
        last_name="Doe",
        created_at=None,
        updated_at=None
    )
    print(f"Created detainee: {detainee.first_name} {detainee.last_name}")
    
    facility = Facility(
        id=None,
        name="Test Facility",
        latitude=34.0522,
        longitude=-118.2437,
        address="123 Test St",
        created_at=None,
        updated_at=None
    )
    print(f"Created facility: {facility.name}")
    
    location_history = DetaineeLocationHistory(
        id=None,
        detainee_id=1,
        facility_id=1,
        start_date=None,
        end_date=None,
        created_at=None
    )
    print(f"Created location history: detainee_id={location_history.detainee_id}, facility_id={location_history.facility_id}")
    
    print("All database models working correctly!")
    
except Exception as e:
    print(f"Error testing database implementation: {e}")
    import traceback
    traceback.print_exc()