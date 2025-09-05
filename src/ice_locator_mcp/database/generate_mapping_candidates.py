#!/usr/bin/env python3
"""
Script to generate a CSV file with facilities that don't have population counts
and candidate TRAC mappings for manual auditing.
"""

import os
import csv
import sys
import re
from typing import List, Dict

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.ice_locator_mcp.database.manager import DatabaseManager
from src.ice_locator_mcp.database.models import Facility
from src.ice_locator_mcp.database.update_facility_population import FacilityPopulationUpdater


def normalize_facility_name(name: str) -> str:
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


def extract_county_and_state(name: str) -> tuple:
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


def find_candidate_matches(trac_facility: Dict, db_facilities: List[Facility], max_candidates: int = 5) -> List[Facility]:
    """
    Find candidate matching facilities in our database for a TRAC facility.
    
    Args:
        trac_facility: Facility data from TRAC
        db_facilities: List of facilities from our database
        max_candidates: Maximum number of candidates to return
        
    Returns:
        List of candidate Facility objects
    """
    candidates = []
    trac_name = trac_facility['name'].upper().strip()
    
    # Try exact match first
    for facility in db_facilities:
        if facility.name.upper().strip() == trac_name:
            return [facility]
    
    # Try normalized name match
    normalized_trac_name = normalize_facility_name(trac_name)
    for facility in db_facilities:
        normalized_db_name = normalize_facility_name(facility.name.upper().strip())
        if normalized_db_name == normalized_trac_name:
            candidates.append(facility)
            if len(candidates) >= max_candidates:
                return candidates
    
    # Try county-based matching
    trac_county, trac_state = extract_county_and_state(trac_name)
    if trac_county:
        for facility in db_facilities:
            db_county, db_state = extract_county_and_state(facility.name)
            if db_county and db_county == trac_county:
                # Check if state matches if available
                if trac_state and db_state:
                    if trac_state == db_state:
                        candidates.append(facility)
                        if len(candidates) >= max_candidates:
                            return candidates
                elif trac_state or db_state:
                    # If only one has state info, check if names contain state
                    facility_name_upper = facility.name.upper()
                    if trac_state and trac_state in facility_name_upper:
                        candidates.append(facility)
                        if len(candidates) >= max_candidates:
                            return candidates
                    elif db_state and db_state in trac_name:
                        candidates.append(facility)
                        if len(candidates) >= max_candidates:
                            return candidates
                else:
                    candidates.append(facility)
                    if len(candidates) >= max_candidates:
                        return candidates
    
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
                candidates.append(facility)
                if len(candidates) >= max_candidates:
                    return candidates
    
    # Try fuzzy matching with token-based approach
    for facility in db_facilities:
        normalized_db_name = normalize_facility_name(facility.name.upper().strip())
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
            
            if similarity_score > 0.3:  # Lower threshold for candidates
                candidates.append(facility)
                if len(candidates) >= max_candidates:
                    return candidates
    
    return candidates


def generate_mapping_candidates():
    """Generate CSV file with facilities without population counts and candidate TRAC mappings."""
    # Get database URL from environment or use default
    database_url = os.environ.get(
        "DATABASE_URL", 
        "postgresql://localhost/ice_locator"
    )
    
    # Connect to database
    db_manager = DatabaseManager(database_url)
    db_manager.connect()
    
    # Get all facilities from our database
    db_facilities = db_manager.get_all_facilities()
    
    # Get facilities without population data
    facilities_without_population = [f for f in db_facilities if f.population_count is None or f.population_count == 0]
    
    print(f"Found {len(facilities_without_population)} facilities without population data")
    
    # Create updater to fetch TRAC data
    updater = FacilityPopulationUpdater(database_url)
    trac_facilities = updater.fetch_trac_data()
    
    if not trac_facilities:
        print("Failed to fetch TRAC data")
        db_manager.disconnect()
        return
    
    print(f"Fetched {len(trac_facilities)} TRAC facilities")
    
    # Generate CSV file
    csv_file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'facility_mapping_candidates.csv')
    csv_file_path = os.path.abspath(csv_file_path)
    
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'db_facility_id', 
            'db_facility_name', 
            'trac_candidates', 
            'trac_count', 
            'trac_state',
            'match_confidence'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        # Process each facility without population data
        for facility in facilities_without_population:
            # Find candidate matches
            candidates = find_candidate_matches(
                {"name": facility.name}, 
                [f for f in trac_facilities if f.get('population_count', 0) > 0],
                max_candidates=3
            )
            
            # Get TRAC facility data for candidates
            trac_candidates = []
            trac_count = ""
            trac_state = ""
            match_confidence = ""
            
            if candidates:
                # For simplicity, we'll just use the first candidate's data
                # In a real implementation, we might want to show all candidates
                first_candidate = candidates[0]
                trac_candidates = "; ".join([f"{c['name']}" for c in candidates[:3]])
                
                # Get the corresponding TRAC data
                for trac_facility in trac_facilities:
                    if trac_facility['name'] == candidates[0]['name']:
                        trac_count = trac_facility.get('population_count', '')
                        trac_state = trac_facility.get('detention_facility_state', '')
                        break
                
                # Calculate a simple confidence score
                normalized_db = normalize_facility_name(facility.name)
                normalized_trac = normalize_facility_name(candidates[0]['name'])
                if normalized_db == normalized_trac:
                    match_confidence = "HIGH"
                elif extract_county_and_state(normalized_db)[0] == extract_county_and_state(normalized_trac)[0]:
                    match_confidence = "MEDIUM"
                else:
                    match_confidence = "LOW"
            
            writer.writerow({
                'db_facility_id': facility.id,
                'db_facility_name': facility.name,
                'trac_candidates': trac_candidates,
                'trac_count': trac_count,
                'trac_state': trac_state,
                'match_confidence': match_confidence
            })
    
    db_manager.disconnect()
    
    print(f"Generated mapping candidates CSV file: {csv_file_path}")
    print("Please manually audit this file to create 1:1 mappings between TRAC and database facilities.")


if __name__ == "__main__":
    generate_mapping_candidates()