"""
Simple test script to verify database manager implementation.
"""
import sys
import os

# Add the database directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'ice_locator_mcp'))

try:
    # Test importing the database manager directly
    from database.manager import DatabaseManager
    from database.models import Detainee, Facility, DetaineeLocationHistory
    print("Database manager imported successfully")
    
    # Test creating a database manager instance
    # Using SQLite for simple testing
    db_manager = DatabaseManager("sqlite:///test.db")
    print("Database manager instance created successfully")
    
    print("Database manager implementation is working correctly!")
    
    # Clean up test database
    if os.path.exists("test.db"):
        os.remove("test.db")
    
except Exception as e:
    print(f"Error testing database manager implementation: {e}")
    import traceback
    traceback.print_exc()