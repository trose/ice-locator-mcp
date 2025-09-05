"""
Script to fetch facility population data from TRAC reports and update the database.
"""
import requests
import json
import re
from typing import List, Dict
from .manager import DatabaseManager
from .models import Facility


class FacilityPopulationUpdater:
    """Updates facility population counts from TRAC reports."""
    
    def __init__(self, database_url: str):
        """
        Initialize the updater.
        
        Args:
            database_url: PostgreSQL connection string
        """
        self.database_url = database_url
        self.db_manager = DatabaseManager(database_url)
    
    def fetch_trac_data(self) -> List[Dict]:
        """
        Fetch facility population data from TRAC reports.
        
        Returns:
            List of facility data dictionaries
        """
        try:
            response = requests.get("https://tracreports.org/immigration/detentionstats/facilities.json")
            response.raise_for_status()
            data = response.json()
            
            # Filter out the "Total" entry and any staging facilities
            facilities = [entry for entry in data if entry['name'] != 'Total' and entry['type_detailed'] != 'STAGING']
            
            # Clean up the count values (remove commas and whitespace)
            for facility in facilities:
                if 'count' in facility and facility['count']:
                    # Remove commas and whitespace, then convert to integer
                    count_str = facility['count'].strip().replace(',', '')
                    facility['population_count'] = int(count_str) if count_str.isdigit() else 0
                else:
                    facility['population_count'] = 0
                    
            return facilities
        except Exception as e:
            print(f"Error fetching TRAC data: {e}")
            return []
    
    def normalize_facility_name(self, name: str) -> str:
        """
        Normalize facility name for matching.
        
        Args:
            name: Facility name
            
        Returns:
            Normalized facility name
        """
        # Remove common suffixes and prefixes
        name = re.sub(r'\s*(DETENTION\s+)?(FACILITY|CENTER|COMPLEX|JAIL|CORRECTIONAL|DET\.?\s+CENTER).*$', '', name, flags=re.IGNORECASE)
        name = re.sub(r'^THE\s+', '', name, flags=re.IGNORECASE)
        
        # Remove extra whitespace
        name = re.sub(r'\s+', ' ', name).strip()
        
        return name
    
    def find_matching_facility(self, trac_facility: Dict, db_facilities: List[Facility]) -> Facility:
        """
        Find a matching facility in our database for a TRAC facility.
        
        Args:
            trac_facility: Facility data from TRAC
            db_facilities: List of facilities from our database
            
        Returns:
            Matching Facility object or None
        """
        trac_name = trac_facility['name'].upper().strip()
        normalized_trac_name = self.normalize_facility_name(trac_name)
        
        # Try exact match first
        for facility in db_facilities:
            if facility.name.upper().strip() == trac_name:
                return facility
        
        # Try normalized name match
        for facility in db_facilities:
            normalized_db_name = self.normalize_facility_name(facility.name.upper().strip())
            if normalized_db_name == normalized_trac_name:
                return facility
                
        # Try partial matching for common patterns
        for facility in db_facilities:
            db_name = facility.name.upper().strip()
            # Check if TRAC name is contained in DB name or vice versa
            if trac_name in db_name or db_name in trac_name:
                return facility
                
        return None
    
    def update_population_counts(self) -> Dict:
        """
        Update population counts for all facilities.
        
        Returns:
            Dictionary with update statistics
        """
        # Connect to database
        self.db_manager.connect()
        
        # Fetch TRAC data
        trac_facilities = self.fetch_trac_data()
        if not trac_facilities:
            print("Failed to fetch TRAC data")
            self.db_manager.disconnect()
            return {"error": "Failed to fetch TRAC data"}
        
        # Get all facilities from our database
        db_facilities = self.db_manager.get_all_facilities()
        
        # Track statistics
        stats = {
            "total_trac_facilities": len(trac_facilities),
            "total_db_facilities": len(db_facilities),
            "matched_facilities": 0,
            "updated_facilities": 0,
            "unmatched_facilities": 0
        }
        
        # Update population counts
        for trac_facility in trac_facilities:
            matching_facility = self.find_matching_facility(trac_facility, db_facilities)
            
            if matching_facility:
                stats["matched_facilities"] += 1
                population_count = trac_facility.get('population_count', 0)
                
                # Update the facility in the database
                success = self.db_manager.update_facility_population(
                    matching_facility.id, 
                    population_count
                )
                
                if success:
                    stats["updated_facilities"] += 1
                    print(f"Updated {matching_facility.name} with population count {population_count}")
                else:
                    print(f"Failed to update {matching_facility.name}")
            else:
                stats["unmatched_facilities"] += 1
                print(f"No match found for TRAC facility: {trac_facility['name']}")
        
        self.db_manager.disconnect()
        
        return stats


def main():
    """Main function to run the population updater."""
    import os
    
    # Get database URL from environment or use default
    database_url = os.environ.get(
        "DATABASE_URL", 
        "postgresql://localhost/ice_locator"
    )
    
    # Create updater and run
    updater = FacilityPopulationUpdater(database_url)
    stats = updater.update_population_counts()
    
    # Print statistics
    print("\nUpdate Statistics:")
    print(f"Total TRAC facilities: {stats.get('total_trac_facilities', 0)}")
    print(f"Total DB facilities: {stats.get('total_db_facilities', 0)}")
    print(f"Matched facilities: {stats.get('matched_facilities', 0)}")
    print(f"Updated facilities: {stats.get('updated_facilities', 0)}")
    print(f"Unmatched facilities: {stats.get('unmatched_facilities', 0)}")


if __name__ == "__main__":
    main()