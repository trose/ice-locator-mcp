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
            
            # Group by facility name and keep only the most recent entry
            facility_dict = {}
            for entry in facilities:
                name = entry['name']
                # Parse the date to determine recency
                try:
                    from datetime import datetime
                    date_str = entry.get('download_date', '01/01/2020')
                    entry_date = datetime.strptime(date_str, '%m/%d/%Y')
                except:
                    entry_date = datetime.min
                
                # Keep the entry with the most recent date
                if name not in facility_dict or entry_date > facility_dict[name]['date']:
                    facility_dict[name] = {
                        'data': entry,
                        'date': entry_date
                    }
            
            # Extract the most recent entries
            facilities = [item['data'] for item in facility_dict.values()]
            
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
        # Convert to uppercase
        name = name.upper()
        
        # Remove punctuation and replace underscores with spaces
        name = re.sub(r'[^\w\s]', ' ', name)
        name = re.sub(r'_', ' ', name)
        
        # Remove common suffixes and prefixes
        name = re.sub(r'\s*(DETENTION\s+)?(FACILITY|CENTER|COMPLEX|JAIL|CORRECTIONAL|DET\.?\s+CENTER|CORRECTIONS?|DEPT\.?|DEPARTMENT|OFFICE|SHERIFF\'?S?|POLICE|LAW ENFORCEMENT|COURT|COUNTY JAIL|COUNTY DETENTION|DET\.?\s+CTR|PROCESSING\s+CENTER|HOLD\s+ROOM|SERVICE\s+PROCESSING|CONTRACT\s+FACILITY|FEDERAL\s+DETENTION|REGIONAL\s+DETENTION|ICE\s+PROCESSING|CORRECTIONAL\s+CENTER|PUBLIC\s+SAFETY|JUSTICE\s+CENTER|DETENTION\s+FACILITY|CORRECTIONAL\s+FACILITY|DETENTION\s+CTR|DETENTION|PROCESSING\s+CTR|SERVICE\s+PROCESSING\s+CENTER|CONTRACT\s+DETENTION|FEDERAL\s+CONTRACT|REGIONAL\s+JAIL|CORRECTIONAL\s+INST|FEDERAL\s+CORR|PUBLIC\s+SAFETY\s+COMPLEX|DET\.?\s+PROCESSING|DET\.?\s+SERV\s+PROC|DET\.?\s+SERV\s+PROCESSING).*$', '', name, flags=re.IGNORECASE)
        name = re.sub(r'^THE\s+', '', name, flags=re.IGNORECASE)
        
        # Remove extra whitespace
        name = re.sub(r'\s+', ' ', name).strip()
        
        return name
    
    def extract_county_and_state(self, name: str) -> tuple:
        """
        Extract county name and state from a facility name.
        
        Args:
            name: Facility name
            
        Returns:
            Tuple of (county_name, state) or (None, None)
        """
        # Extract county name
        county_match = re.search(r'([A-Z]+(?:\s+[A-Z]+)*?)\s+COUNTY', name.upper())
        county_name = county_match.group(1) if county_match else None
        
        # Extract state from the end of the name (after comma) or from parentheses
        state_match = re.search(r',\s*([A-Z]+)$', name)
        if not state_match:
            state_match = re.search(r'\(([A-Z]+)\)', name)
        state = state_match.group(1) if state_match else None
        
        return (county_name, state)
    
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
        
        # Try exact match first
        for facility in db_facilities:
            if facility.name.upper().strip() == trac_name:
                return facility
        
        # Try normalized name match
        normalized_trac_name = self.normalize_facility_name(trac_name)
        for facility in db_facilities:
            normalized_db_name = self.normalize_facility_name(facility.name.upper().strip())
            if normalized_db_name == normalized_trac_name:
                return facility
                
        # Try county-based matching
        trac_county, trac_state = self.extract_county_and_state(trac_name)
        if trac_county:
            for facility in db_facilities:
                db_county, db_state = self.extract_county_and_state(facility.name)
                if db_county and db_county == trac_county:
                    # Check if state matches if available
                    if trac_state and db_state:
                        if trac_state == db_state:
                            return facility
                    elif trac_state or db_state:
                        # If only one has state info, check if names contain state
                        facility_name_upper = facility.name.upper()
                        if trac_state and trac_state in facility_name_upper:
                            return facility
                        elif db_state and db_state in trac_name:
                            return facility
                    else:
                        return facility
        
        # Try partial token matching - check if TRAC tokens are contained in DB name
        trac_tokens = set(normalized_trac_name.split())
        if len(trac_tokens) > 0:
            for facility in db_facilities:
                facility_name_upper = facility.name.upper()
                # Check if all TRAC tokens are in the facility name
                match_count = 0
                for token in trac_tokens:
                    if token in facility_name_upper:
                        match_count += 1
                
                # If we match at least 2 tokens and it's more than 50% of TRAC tokens
                if match_count >= 2 and match_count / len(trac_tokens) >= 0.5:
                    return facility
        
        # Try fuzzy matching with token-based approach
        for facility in db_facilities:
            normalized_db_name = self.normalize_facility_name(facility.name.upper().strip())
            db_tokens = set(normalized_db_name.split())
            
            # Calculate similarity score based on common tokens
            if len(trac_tokens) > 0 and len(db_tokens) > 0:
                common_tokens = trac_tokens.intersection(db_tokens)
                total_tokens = trac_tokens.union(db_tokens)
                
                similarity_score = len(common_tokens) / len(total_tokens)
                
                # Look for county matches specifically
                trac_has_county = 'COUNTY' in trac_tokens
                db_has_county = 'COUNTY' in db_tokens
                
                if trac_has_county and db_has_county:
                    # Boost score for county matches
                    similarity_score *= 1.5
                
                # Look for state matches
                trac_states = {token for token in trac_tokens if len(token) == 2 and token.isalpha()}
                db_states = {token for token in db_tokens if len(token) == 2 and token.isalpha()}
                
                if trac_states and db_states and trac_states.intersection(db_states):
                    # Boost score for state matches
                    similarity_score *= 1.2
                
                if similarity_score > 0.4:  # Threshold for matching
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