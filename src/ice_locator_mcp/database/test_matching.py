#!/usr/bin/env python3
"""
Test script for facility name matching algorithm.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ice_locator_mcp.database.update_facility_population import FacilityPopulationUpdater
from src.ice_locator_mcp.database.models import Facility

def test_matching():
    """Test the matching algorithm with sample data."""
    # Create a mock updater
    updater = FacilityPopulationUpdater("postgresql://localhost/ice_locator")
    
    # Sample TRAC facilities
    trac_facilities = [
        {"name": "ALAMANCE COUNTY DETENTION FACILITY", "detention_facility_state": "NC"},
        {"name": "BAKER COUNTY SHERIFF DEPT.", "detention_facility_state": "FL"},
        {"name": "ALLEGANY COUNTY JAIL", "detention_facility_state": "NY"},
        {"name": "BROWARD TRANSITIONAL CENTER", "detention_facility_state": "FL"},
        {"name": "ORANGE COUNTY JAIL (FL)", "detention_facility_state": "FL"},
    ]
    
    # Sample database facilities
    db_facilities = [
        Facility(id=1, name="Alamance County Sheriff's Office, NORTH CAROLINA", latitude=0.0, longitude=0.0, address=None),
        Facility(id=2, name="Baker County Sheriff's Office, FLORIDA", latitude=0.0, longitude=0.0, address=None),
        Facility(id=3, name="Allegany County Sheriff's Office, MARYLAND", latitude=0.0, longitude=0.0, address=None),
        Facility(id=4, name="Broward Transitional Center", latitude=0.0, longitude=0.0, address=None),
        Facility(id=5, name="Orange County Sheriff's Office, FLORIDA", latitude=0.0, longitude=0.0, address=None),
        Facility(id=6, name="Orange County Jail", latitude=0.0, longitude=0.0, address=None),
    ]
    
    print("Testing facility matching algorithm:")
    print("=" * 50)
    
    for trac_facility in trac_facilities:
        print(f"\nTRAC Facility: {trac_facility['name']}")
        match = updater.find_matching_facility(trac_facility, db_facilities)
        if match:
            print(f"  Matched: {match.name}")
        else:
            print("  No match found")
            
        # Test normalization
        normalized = updater.normalize_facility_name(trac_facility['name'])
        print(f"  Normalized: {normalized}")
        
        # Test county extraction
        county, state = updater.extract_county_and_state(trac_facility['name'])
        print(f"  County: {county}, State: {state}")

if __name__ == "__main__":
    test_matching()