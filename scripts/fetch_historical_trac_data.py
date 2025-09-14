#!/usr/bin/env python3
"""
Historical TRAC Data Fetcher
Fetches complete historical facility population data from TRAC Reports
going back to September 30, 2019 as specified in the success metrics.
"""

import requests
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import time
import logging
from dataclasses import dataclass
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TRACFacility:
    """Represents a facility record from TRAC data."""
    name: str
    city: str
    state: str
    zip_code: str
    facility_type: str
    population_count: int
    download_date: str
    guaranteed_min_num: Optional[int] = None

class HistoricalTRACDataFetcher:
    """Fetches and processes historical TRAC facility data."""
    
    def __init__(self, db_path: str = "ice_locator_facilities.db"):
        self.db_path = db_path
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.base_url = "https://tracreports.org/immigration/detentionstats/facilities.json"
        
    def fetch_trac_data(self) -> List[Dict]:
        """Fetch all TRAC facility data."""
        logger.info("Fetching TRAC facility data...")
        
        try:
            response = self.session.get(self.base_url, timeout=30)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Successfully fetched {len(data)} records from TRAC")
            return data
        except requests.RequestException as e:
            logger.error(f"Failed to fetch TRAC data: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse TRAC JSON data: {e}")
            raise
    
    def parse_facility_record(self, record: Dict) -> Optional[TRACFacility]:
        """Parse a single facility record from TRAC data."""
        try:
            # Extract and clean population count
            count_str = record.get('count', '0').strip()
            population_count = 0
            
            if count_str:
                # Remove spaces and commas, then convert to int
                # TRAC data format: "               2,172" -> "2172"
                cleaned_count = count_str.replace(',', '').replace(' ', '')
                if cleaned_count.isdigit():
                    population_count = int(cleaned_count)
            
            # Skip facilities with no population
            if population_count == 0:
                return None
            
            # Extract guaranteed minimum number
            guaranteed_min = record.get('guaranteed_min_num')
            if guaranteed_min is not None:
                try:
                    guaranteed_min = int(guaranteed_min)
                except (ValueError, TypeError):
                    guaranteed_min = None
            
            return TRACFacility(
                name=record.get('name', '').strip(),
                city=record.get('detention_facility_city', '').strip(),
                state=record.get('detention_facility_state', '').strip(),
                zip_code=record.get('detention_facility_zip', '').strip(),
                facility_type=record.get('type_detailed', '').strip(),
                population_count=population_count,
                download_date=record.get('download_date', '').strip(),
                guaranteed_min_num=guaranteed_min
            )
        except Exception as e:
            logger.warning(f"Failed to parse facility record: {e}")
            return None
    
    def parse_download_date(self, date_str: str) -> Optional[datetime]:
        """Parse TRAC download date string to datetime object."""
        try:
            # TRAC dates are in MM/DD/YYYY format
            return datetime.strptime(date_str, '%m/%d/%Y')
        except ValueError:
            logger.warning(f"Invalid date format: {date_str}")
            return None
    
    def filter_historical_data(self, facilities: List[TRACFacility], start_date: datetime) -> List[TRACFacility]:
        """Filter facilities to only include data from start_date onwards."""
        filtered = []
        for facility in facilities:
            facility_date = self.parse_download_date(facility.download_date)
            if facility_date and facility_date >= start_date:
                filtered.append(facility)
        
        logger.info(f"Filtered to {len(filtered)} facilities from {start_date.strftime('%Y-%m-%d')} onwards")
        return filtered
    
    def group_by_month(self, facilities: List[TRACFacility]) -> Dict[str, List[TRACFacility]]:
        """Group facilities by month-year for monthly data organization."""
        monthly_data = {}
        
        for facility in facilities:
            facility_date = self.parse_download_date(facility.download_date)
            if facility_date:
                month_key = facility_date.strftime('%Y-%m')
                if month_key not in monthly_data:
                    monthly_data[month_key] = []
                monthly_data[month_key].append(facility)
        
        logger.info(f"Grouped data into {len(monthly_data)} months")
        return monthly_data
    
    def normalize_facility_name(self, name: str) -> str:
        """Normalize facility names for better matching."""
        # Remove common suffixes and normalize
        name = name.upper().strip()
        name = re.sub(r'\s+(ICE|DETENTION|CENTER|FACILITY|JAIL|CORRECTIONAL|CORRECTIONS)\s*$', '', name)
        name = re.sub(r'\s+', ' ', name)  # Normalize whitespace
        return name.strip()
    
    def normalize_facility_name_advanced(self, name: str) -> str:
        """Advanced normalization with abbreviation handling."""
        name = name.upper().strip()
        
        # Handle common abbreviations and variations
        abbreviations = {
            'DET': 'DETENTION',
            'DETENTION': 'DETENTION',
            'CORRECTIONAL': 'DETENTION',  # Map correctional to detention for matching
            'CORRECTIONS': 'DETENTION',   # Map corrections to detention for matching
            'CENTER': 'CENTER',
            'CENTRE': 'CENTER',
            'FACILITY': 'FACILITY',
            'JAIL': 'DETENTION',          # Map jail to detention for matching
            'PRISON': 'DETENTION',        # Map prison to detention for matching
            'PROCESSING': 'PROCESSING',
            'SERVICE': 'SERVICE',
            'ICE': 'ICE'
        }
        
        # Replace abbreviations with standardized terms
        for abbrev, standard in abbreviations.items():
            name = re.sub(r'\b' + abbrev + r'\b', standard, name)
        
        # Remove common suffixes
        name = re.sub(r'\s+(ICE|DETENTION|CENTER|FACILITY|PROCESSING|SERVICE)\s*$', '', name)
        name = re.sub(r'\s+', ' ', name)  # Normalize whitespace
        return name.strip()
    
    def extract_location_from_address(self, address: str) -> tuple:
        """Extract city and state from address string."""
        if not address:
            return None, None
        
        # Common patterns: "City, State, ZIP" or "City, State ZIP"
        parts = [part.strip() for part in address.split(',')]
        if len(parts) >= 2:
            city = parts[0].strip()
            state_zip = parts[1].strip()
            # Extract state (first 2 characters)
            state = state_zip[:2] if len(state_zip) >= 2 else None
            return city, state
        
        return None, None
    
    def match_facility_to_database(self, trac_facility: TRACFacility, db_facilities: List[Dict]) -> Optional[Dict]:
        """Match TRAC facility to database facility using improved strategies."""
        trac_name_normalized = self.normalize_facility_name(trac_facility.name)
        trac_name_advanced = self.normalize_facility_name_advanced(trac_facility.name)
        
        # Strategy 1: Exact name match (original)
        for db_facility in db_facilities:
            db_name_normalized = self.normalize_facility_name(db_facility['name'])
            if trac_name_normalized == db_name_normalized:
                return db_facility
        
        # Strategy 2: Advanced normalization match
        for db_facility in db_facilities:
            db_name_advanced = self.normalize_facility_name_advanced(db_facility['name'])
            if trac_name_advanced == db_name_advanced:
                return db_facility
        
        # Strategy 3: Partial name match with advanced normalization
        for db_facility in db_facilities:
            db_name_advanced = self.normalize_facility_name_advanced(db_facility['name'])
            if (trac_name_advanced in db_name_advanced or 
                db_name_advanced in trac_name_advanced):
                return db_facility
        
        # Strategy 4: Location-based matching with address parsing
        for db_facility in db_facilities:
            # Try direct state/city match first
            if (trac_facility.state == db_facility.get('state', '') and
                trac_facility.city.upper() == db_facility.get('city', '').upper()):
                return db_facility
            
            # Try address parsing for database facility
            db_city, db_state = self.extract_location_from_address(db_facility.get('address', ''))
            if (db_city and db_state and
                trac_facility.state == db_state and
                trac_facility.city.upper() == db_city.upper()):
                return db_facility
        
        # Strategy 5: Fuzzy matching for similar names
        for db_facility in db_facilities:
            db_name_advanced = self.normalize_facility_name_advanced(db_facility['name'])
            # Check if the core parts match (excluding common words)
            trac_core = re.sub(r'\b(COUNTY|CITY|TOWN|VILLAGE)\b', '', trac_name_advanced).strip()
            db_core = re.sub(r'\b(COUNTY|CITY|TOWN|VILLAGE)\b', '', db_name_advanced).strip()
            
            if trac_core and db_core and (
                trac_core in db_core or db_core in trac_core or
                len(set(trac_core.split()) & set(db_core.split())) >= 2
            ):
                return db_facility
        
        return None
    
    def get_database_facilities(self) -> List[Dict]:
        """Get all facilities from the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, latitude, longitude, address, population_count
            FROM facilities
        """)
        
        facilities = []
        for row in cursor.fetchall():
            # Extract city and state from address for better matching
            city, state = self.extract_location_from_address(row[4])
            
            facilities.append({
                'id': row[0],
                'name': row[1],
                'latitude': row[2],
                'longitude': row[3],
                'address': row[4],
                'population_count': row[5],
                'city': city,
                'state': state
            })
        
        conn.close()
        return facilities
    
    def apply_entity_discernment_algorithm(self, facility_records: List[TRACFacility]) -> TRACFacility:
        """
        Apply entity discernment algorithm to resolve multiple records for the same facility.
        
        Strategy:
        1. If multiple records exist for the same facility, take the most recent record
        2. Keep the most recent download_date and population count
        3. This handles cases where facilities have multiple data collection points or updates
        """
        if not facility_records:
            return None
        
        if len(facility_records) == 1:
            return facility_records[0]
        
        # Find the most recent record (by download_date)
        most_recent = max(facility_records, key=lambda r: r.download_date)
        
        logger.debug(f"Entity discernment: {most_recent.name} - {len(facility_records)} records, using most recent: {most_recent.download_date} with population {most_recent.population_count}")
        return most_recent

    def update_database_with_monthly_data(self, monthly_data: Dict[str, List[TRACFacility]]):
        """Update database with monthly population data using entity discernment algorithm."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get existing facilities
        db_facilities = self.get_database_facilities()
        
        # Create monthly_population table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS monthly_population (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                facility_id INTEGER,
                month_year TEXT,
                population_count INTEGER,
                download_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (facility_id) REFERENCES facilities (id)
            )
        """)
        
        # Create unique index to prevent duplicates
        try:
            cursor.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_monthly_population_unique 
                ON monthly_population(facility_id, month_year)
            """)
        except sqlite3.OperationalError:
            # Index might already exist, continue
            pass
        
        # Clear existing monthly data
        cursor.execute("DELETE FROM monthly_population")
        
        total_records = 0
        matched_facilities = 0
        entity_discernment_applied = 0
        
        for month_year, facilities in monthly_data.items():
            logger.info(f"Processing {month_year}: {len(facilities)} facilities")
            
            # Group facilities by name for entity discernment
            facility_groups = {}
            for trac_facility in facilities:
                # Use normalized name as key for grouping
                normalized_name = self.normalize_facility_name_advanced(trac_facility.name)
                if normalized_name not in facility_groups:
                    facility_groups[normalized_name] = []
                facility_groups[normalized_name].append(trac_facility)
            
            # Apply entity discernment and process each group
            for normalized_name, facility_group in facility_groups.items():
                # Apply entity discernment algorithm
                resolved_facility = self.apply_entity_discernment_algorithm(facility_group)
                
                if len(facility_group) > 1:
                    entity_discernment_applied += 1
                    logger.debug(f"Applied entity discernment to {resolved_facility.name}: {len(facility_group)} records -> 1 record")
                
                # Match to database facility
                db_facility = self.match_facility_to_database(resolved_facility, db_facilities)
                
                if db_facility:
                    # Use INSERT OR REPLACE to handle potential duplicates
                    cursor.execute("""
                        INSERT OR REPLACE INTO monthly_population 
                        (facility_id, month_year, population_count, download_date)
                        VALUES (?, ?, ?, ?)
                    """, (
                        db_facility['id'],
                        month_year,
                        resolved_facility.population_count,
                        resolved_facility.download_date
                    ))
                    matched_facilities += 1
                else:
                    # This is expected behavior - many TRAC facilities are not in our ICE-focused database
                    logger.debug(f"TRAC facility not in ICE database: {resolved_facility.name}")
                
                total_records += 1
        
        conn.commit()
        conn.close()
        
        unmatched_facilities = total_records - matched_facilities
        logger.info(f"Updated database with {total_records} records, matched {matched_facilities} facilities")
        logger.info(f"Applied entity discernment to {entity_discernment_applied} facility groups")
        logger.info(f"Unmatched facilities: {unmatched_facilities} (expected - these are non-ICE facilities like county jails)")
    
    def export_monthly_data_for_frontend(self, output_file: str = "web-app/src/data/facilities_monthly_optimized.json"):
        """Export monthly data in the format expected by the frontend."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all facilities with their monthly data
        cursor.execute("""
            SELECT 
                f.id, f.name, f.latitude, f.longitude, f.address,
                mp.month_year, mp.population_count
            FROM facilities f
            LEFT JOIN monthly_population mp ON f.id = mp.facility_id
            ORDER BY f.name, mp.month_year
        """)
        
        facilities_data = {}
        available_months = set()
        
        for row in cursor.fetchall():
            facility_id, name, lat, lng, address, month_year, population = row
            
            if facility_id not in facilities_data:
                facilities_data[facility_id] = {
                    'id': facility_id,
                    'name': name,
                    'latitude': lat,
                    'longitude': lng,
                    'address': address or '',
                    'monthly_population': {}
                }
            
            if month_year and population is not None:
                facilities_data[facility_id]['monthly_population'][month_year] = population
                available_months.add(month_year)
        
        # Convert to list and sort months
        facilities_list = list(facilities_data.values())
        available_months_list = sorted(list(available_months))
        latest_month = available_months_list[-1] if available_months_list else None
        
        # Create optimized frontend data structure
        # Convert facilities to optimized format
        optimized_facilities = []
        for facility in facilities_list:
            optimized_facilities.append({
                'i': facility['id'],  # id (shortened key)
                'n': facility['name'],  # name (shortened key)
                'lat': facility['latitude'],  # latitude (shortened key)
                'lng': facility['longitude'],  # longitude (shortened key)
                'a': facility['address']  # address (shortened key)
            })
        
        # Convert monthly data to optimized format
        optimized_data = {}
        for facility in facilities_list:
            facility_id = facility['id']
            monthly_population = facility['monthly_population']
            population_array = []
            for month in available_months_list:
                population_array.append(monthly_population.get(month, 0))
            optimized_data[facility_id] = population_array
        
        frontend_data = {
            'meta': {
                'v': 1,  # version
                't': datetime.now().isoformat(),  # timestamp
                'f': len(optimized_facilities),  # facility count
                'm': available_months_list,  # available months
                'l': latest_month,  # latest month
                'd': 'ICE Detention Facilities - Optimized Monthly Data'
            },
            'facilities': optimized_facilities,
            'data': optimized_data
        }
        
        # Write to file with no spaces for smaller file size
        with open(output_file, 'w') as f:
            json.dump(frontend_data, f, separators=(',', ':'))
        
        conn.close()
        
        logger.info(f"Exported monthly data to {output_file}")
        logger.info(f"Total facilities: {len(facilities_list)}")
        logger.info(f"Available months: {len(available_months_list)}")
        logger.info(f"Latest month: {latest_month}")
    
    def run_historical_data_collection(self, start_date_str: str = "2019-09-30"):
        """Main method to collect and process all historical data."""
        logger.info(f"Starting historical data collection from {start_date_str}")
        
        # Parse start date
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        
        # Fetch TRAC data
        raw_data = self.fetch_trac_data()
        
        # Parse facility records
        facilities = []
        for record in raw_data:
            facility = self.parse_facility_record(record)
            if facility:
                facilities.append(facility)
        
        logger.info(f"Parsed {len(facilities)} facility records")
        
        # Filter to historical data
        historical_facilities = self.filter_historical_data(facilities, start_date)
        
        # Group by month
        monthly_data = self.group_by_month(historical_facilities)
        
        # Update database
        self.update_database_with_monthly_data(monthly_data)
        
        # Export for frontend
        self.export_monthly_data_for_frontend()
        
        logger.info("Historical data collection completed successfully")

def main():
    """Main entry point."""
    fetcher = HistoricalTRACDataFetcher()
    
    try:
        fetcher.run_historical_data_collection()
    except Exception as e:
        logger.error(f"Historical data collection failed: {e}")
        raise

if __name__ == "__main__":
    main()
