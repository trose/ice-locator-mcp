"""
Script to check that facility population data was properly updated.
"""
import os
from .manager import DatabaseManager


def check_population_updates():
    """Check that facility population data was properly updated."""
    # Get database URL from environment or use default
    database_url = os.environ.get(
        "DATABASE_URL", 
        "postgresql://localhost/ice_locator"
    )
    
    # Connect to database
    db_manager = DatabaseManager(database_url)
    db_manager.connect()
    
    # Get facilities with population counts
    facilities = db_manager.get_all_facilities()
    
    # Count facilities with and without population data
    facilities_with_population = [f for f in facilities if f.population_count is not None and f.population_count > 0]
    facilities_without_population = [f for f in facilities if f.population_count is None or f.population_count == 0]
    
    print(f"Total facilities: {len(facilities)}")
    print(f"Facilities with population data: {len(facilities_with_population)}")
    print(f"Facilities without population data: {len(facilities_without_population)}")
    
    # Show some examples
    print("\nFacilities with population data (first 10):")
    for facility in facilities_with_population[:10]:
        print(f"  {facility.name}: {facility.population_count}")
    
    # Show some facilities without population data
    print("\nFacilities without population data (first 10):")
    for facility in facilities_without_population[:10]:
        print(f"  {facility.name}: {facility.population_count}")
    
    db_manager.disconnect()


if __name__ == "__main__":
    check_population_updates()