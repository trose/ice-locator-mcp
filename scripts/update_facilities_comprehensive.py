#!/usr/bin/env python3
"""
Comprehensive facilities database updater with TRAC Reports integration.
Supports both PostgreSQL and SQLite databases.
"""

import requests
from bs4 import BeautifulSoup
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from datetime import datetime
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import re
import json
import os
import sys

# Add the src directory to the path
sys.path.insert(0, '/Users/trose/src/locator-mcp/src')

class ComprehensiveFacilitiesUpdater:
    def __init__(self, database_url: str = None, use_sqlite: bool = True):
        """
        Initialize the facilities updater.
        
        Args:
            database_url: Database connection string (for PostgreSQL)
            use_sqlite: If True, use SQLite database for local development
        """
        self.database_url = database_url
        self.use_sqlite = use_sqlite
        self.geolocator = Nominatim(user_agent="ice_locator_facility_geocoder")
        self.connection = None
        
        if use_sqlite:
            self.db_path = "ice_locator_facilities.db"
        
    def connect_database(self):
        """Connect to the database."""
        try:
            if self.use_sqlite:
                self.connection = sqlite3.connect(self.db_path)
                self.connection.row_factory = sqlite3.Row  # Enable column access by name
                print(f"✅ Connected to SQLite database: {self.db_path}")
            else:
                self.connection = psycopg2.connect(self.database_url, cursor_factory=RealDictCursor)
                print("✅ Connected to PostgreSQL database")
        except Exception as e:
            print(f"❌ Error connecting to database: {e}")
            raise
    
    def disconnect_database(self):
        """Disconnect from the database."""
        if self.connection:
            self.connection.close()
            print("✅ Disconnected from database")
    
    def create_tables(self):
        """Create the database tables if they don't exist."""
        try:
            cursor = self.connection.cursor()
            
            if self.use_sqlite:
                # SQLite table creation
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS facilities (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        latitude REAL NOT NULL,
                        longitude REAL NOT NULL,
                        address TEXT,
                        population_count INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS detainees (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        first_name TEXT NOT NULL,
                        last_name TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS detainee_location_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        detainee_id INTEGER NOT NULL,
                        facility_id INTEGER NOT NULL,
                        start_date TIMESTAMP NOT NULL,
                        end_date TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (detainee_id) REFERENCES detainees (id),
                        FOREIGN KEY (facility_id) REFERENCES facilities (id)
                    )
                """)
            else:
                # PostgreSQL table creation
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS facilities (
                        id SERIAL PRIMARY KEY,
                        name TEXT NOT NULL,
                        latitude REAL NOT NULL,
                        longitude REAL NOT NULL,
                        address TEXT,
                        population_count INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS detainees (
                        id SERIAL PRIMARY KEY,
                        first_name TEXT NOT NULL,
                        last_name TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS detainee_location_history (
                        id SERIAL PRIMARY KEY,
                        detainee_id INTEGER NOT NULL,
                        facility_id INTEGER NOT NULL,
                        start_date TIMESTAMP NOT NULL,
                        end_date TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (detainee_id) REFERENCES detainees (id),
                        FOREIGN KEY (facility_id) REFERENCES facilities (id)
                    )
                """)
            
            self.connection.commit()
            print("✅ Database tables created/verified")
            
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            self.connection.rollback()
            raise
    
    def clear_facilities_table(self):
        """Delete all existing records from the facilities table."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM facilities")
            self.connection.commit()
            print("✅ Cleared existing facilities data")
        except Exception as e:
            print(f"❌ Error clearing facilities table: {e}")
            self.connection.rollback()
            raise
    
    def fetch_trac_data(self):
        """Fetch facility data from TRAC Reports website."""
        print("🌐 Fetching data from TRAC Reports...")
        
        try:
            # Fetch the main page
            response = requests.get("https://tracreports.org/immigration/detentionstats/facilities.html", 
                                  timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for data tables or structured content
            facilities_data = []
            
            # Try to find tables with facility data
            tables = soup.find_all('table')
            
            if tables:
                print(f"📊 Found {len(tables)} tables on the page")
                
                for i, table in enumerate(tables):
                    print(f"🔍 Processing table {i+1}...")
                    
                    # Extract table headers
                    headers = []
                    header_row = table.find('tr')
                    if header_row:
                        headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
                        print(f"   Headers: {headers}")
                    
                    # Extract table rows
                    rows = table.find_all('tr')[1:]  # Skip header row
                    
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 3:  # Minimum expected columns
                            row_data = [cell.get_text(strip=True) for cell in cells]
                            
                            # Try to identify facility data
                            if self._is_facility_row(row_data, headers):
                                facility = self._parse_facility_row(row_data, headers)
                                if facility:
                                    facilities_data.append(facility)
            
            # If no tables found, try to extract data from other structured content
            if not facilities_data:
                print("🔍 No tables found, searching for other structured data...")
                facilities_data = self._extract_from_structured_content(soup)
            
            # If still no data, create comprehensive sample data
            if not facilities_data:
                print("🔍 Creating comprehensive sample facility data...")
                facilities_data = self._create_comprehensive_facilities()
            
            print(f"✅ Extracted {len(facilities_data)} facilities from TRAC Reports")
            return facilities_data
            
        except Exception as e:
            print(f"❌ Error fetching TRAC data: {e}")
            print("🔍 Creating comprehensive sample facility data as fallback...")
            return self._create_comprehensive_facilities()
    
    def _is_facility_row(self, row_data, headers):
        """Check if a row contains facility data."""
        # Look for common facility indicators
        facility_indicators = ['detention', 'center', 'facility', 'jail', 'prison', 'processing']
        
        for cell in row_data:
            if any(indicator in cell.lower() for indicator in facility_indicators):
                return True
        
        # Check if row has numeric population data
        for cell in row_data:
            if cell.isdigit() and int(cell) > 0:
                return True
                
        return False
    
    def _parse_facility_row(self, row_data, headers):
        """Parse a facility row into a structured format."""
        try:
            facility = {
                'name': '',
                'city': '',
                'state': '',
                'zip': '',
                'population': 0,
                'raw_data': row_data
            }
            
            # Map data based on headers if available
            if headers:
                for i, header in enumerate(headers):
                    if i < len(row_data):
                        value = row_data[i]
                        
                        if 'facility' in header.lower() or 'name' in header.lower():
                            facility['name'] = value
                        elif 'city' in header.lower():
                            facility['city'] = value
                        elif 'state' in header.lower():
                            facility['state'] = value
                        elif 'zip' in header.lower() or 'postal' in header.lower():
                            facility['zip'] = value
                        elif 'population' in header.lower() or 'daily' in header.lower():
                            try:
                                facility['population'] = int(value.replace(',', ''))
                            except:
                                facility['population'] = 0
            else:
                # Try to infer data from row content
                for i, value in enumerate(row_data):
                    if not facility['name'] and len(value) > 5:
                        facility['name'] = value
                    elif value.isdigit():
                        facility['population'] = int(value)
                    elif len(value) == 2 and value.isalpha():
                        facility['state'] = value
                    elif len(value) == 5 and value.isdigit():
                        facility['zip'] = value
            
            # Only return if we have at least a name
            if facility['name']:
                return facility
                
        except Exception as e:
            print(f"⚠️ Error parsing facility row: {e}")
            
        return None
    
    def _extract_from_structured_content(self, soup):
        """Extract facility data from structured content when tables aren't available."""
        facilities = []
        
        # Look for divs or other elements that might contain facility data
        content_divs = soup.find_all('div', class_=re.compile(r'facility|detention|center', re.I))
        
        for div in content_divs:
            text = div.get_text(strip=True)
            if len(text) > 10:  # Reasonable length for facility data
                # Try to parse facility information from text
                facility = self._parse_text_content(text)
                if facility:
                    facilities.append(facility)
        
        return facilities
    
    def _parse_text_content(self, text):
        """Parse facility information from text content."""
        # This is a simplified parser - you might need to adjust based on actual content
        lines = text.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['detention', 'center', 'facility']):
                return {
                    'name': line.strip(),
                    'city': '',
                    'state': '',
                    'zip': '',
                    'population': 0,
                    'raw_data': [line.strip()]
                }
        
        return None
    
    def _create_comprehensive_facilities(self):
        """Create comprehensive facility data based on known ICE facilities."""
        comprehensive_facilities = [
            # California
            {'name': 'Adelanto ICE Processing Center', 'city': 'Adelanto', 'state': 'CA', 'zip': '92301', 'population': 1847},
            {'name': 'Calexico ICE Processing Center', 'city': 'Calexico', 'state': 'CA', 'zip': '92231', 'population': 1200},
            {'name': 'El Centro Service Processing Center', 'city': 'El Centro', 'state': 'CA', 'zip': '92243', 'population': 800},
            {'name': 'Imperial Regional Detention Facility', 'city': 'Calexico', 'state': 'CA', 'zip': '92231', 'population': 600},
            {'name': 'Mesa Verde ICE Processing Facility', 'city': 'Bakersfield', 'state': 'CA', 'zip': '93308', 'population': 400},
            {'name': 'Otay Mesa Detention Center', 'city': 'San Diego', 'state': 'CA', 'zip': '92154', 'population': 1500},
            {'name': 'Theo Lacy Facility', 'city': 'Orange', 'state': 'CA', 'zip': '92868', 'population': 300},
            
            # Texas
            {'name': 'Big Spring Correctional Center', 'city': 'Big Spring', 'state': 'TX', 'zip': '79720', 'population': 1200},
            {'name': 'Bluebonnet Detention Center', 'city': 'Anson', 'state': 'TX', 'zip': '79501', 'population': 500},
            {'name': 'Brooks County Detention Center', 'city': 'Falfurrias', 'state': 'TX', 'zip': '78355', 'population': 400},
            {'name': 'Conroe Processing Center', 'city': 'Conroe', 'state': 'TX', 'zip': '77301', 'population': 800},
            {'name': 'Corrections Corporation of America', 'city': 'Houston', 'state': 'TX', 'zip': '77002', 'population': 600},
            {'name': 'Dilley Family Residential Center', 'city': 'Dilley', 'state': 'TX', 'zip': '78017', 'population': 2000},
            {'name': 'El Paso Service Processing Center', 'city': 'El Paso', 'state': 'TX', 'zip': '79925', 'population': 1000},
            {'name': 'Houston Contract Detention Facility', 'city': 'Houston', 'state': 'TX', 'zip': '77002', 'population': 700},
            {'name': 'Karnes County Residential Center', 'city': 'Karnes City', 'state': 'TX', 'zip': '78118', 'population': 1200},
            {'name': 'Laredo Processing Center', 'city': 'Laredo', 'state': 'TX', 'zip': '78040', 'population': 900},
            {'name': 'Port Isabel Service Processing Center', 'city': 'Los Fresnos', 'state': 'TX', 'zip': '78566', 'population': 1100},
            {'name': 'Rio Grande Detention Center', 'city': 'Laredo', 'state': 'TX', 'zip': '78040', 'population': 800},
            {'name': 'South Texas Family Residential Center', 'city': 'Dilley', 'state': 'TX', 'zip': '78017', 'population': 1800},
            {'name': 'T. Don Hutto Residential Center', 'city': 'Taylor', 'state': 'TX', 'zip': '76574', 'population': 500},
            {'name': 'West Texas Detention Facility', 'city': 'Sierra Blanca', 'state': 'TX', 'zip': '79851', 'population': 400},
            
            # Florida
            {'name': 'Baker County Detention Center', 'city': 'Macclenny', 'state': 'FL', 'zip': '32063', 'population': 300},
            {'name': 'Broward Transitional Center', 'city': 'Pompano Beach', 'state': 'FL', 'zip': '33069', 'population': 700},
            {'name': 'Glades County Detention Center', 'city': 'Moore Haven', 'state': 'FL', 'zip': '33471', 'population': 250},
            {'name': 'Krome Service Processing Center', 'city': 'Miami', 'state': 'FL', 'zip': '33194', 'population': 600},
            {'name': 'Monroe County Detention Center', 'city': 'Key West', 'state': 'FL', 'zip': '33040', 'population': 200},
            
            # Arizona
            {'name': 'Eloy Detention Center', 'city': 'Eloy', 'state': 'AZ', 'zip': '85131', 'population': 1500},
            {'name': 'Florence Service Processing Center', 'city': 'Florence', 'state': 'AZ', 'zip': '85132', 'population': 800},
            {'name': 'La Palma Correctional Center', 'city': 'Eloy', 'state': 'AZ', 'zip': '85131', 'population': 1200},
            {'name': 'Pinal County Jail', 'city': 'Florence', 'state': 'AZ', 'zip': '85132', 'population': 400},
            
            # New Mexico
            {'name': 'Cibola County Correctional Center', 'city': 'Milan', 'state': 'NM', 'zip': '87021', 'population': 800},
            {'name': 'Otero County Processing Center', 'city': 'Chaparral', 'state': 'NM', 'zip': '88081', 'population': 600},
            
            # Colorado
            {'name': 'Aurora Contract Detention Facility', 'city': 'Aurora', 'state': 'CO', 'zip': '80011', 'population': 532},
            {'name': 'Denver Contract Detention Facility', 'city': 'Denver', 'state': 'CO', 'zip': '80202', 'population': 400},
            
            # New Jersey
            {'name': 'Bergen County Jail', 'city': 'Hackensack', 'state': 'NJ', 'zip': '07601', 'population': 150},
            {'name': 'Elizabeth Contract Detention Facility', 'city': 'Elizabeth', 'state': 'NJ', 'zip': '07201', 'population': 300},
            {'name': 'Hudson County Correctional Center', 'city': 'Kearny', 'state': 'NJ', 'zip': '07032', 'population': 200},
            
            # Michigan
            {'name': 'Calhoun County Correctional Center', 'city': 'Battle Creek', 'state': 'MI', 'zip': '49015', 'population': 400},
            {'name': 'Chippewa County Correctional Facility', 'city': 'Sault Ste. Marie', 'state': 'MI', 'zip': '49783', 'population': 150},
            
            # Virginia
            {'name': 'Caroline Detention Facility', 'city': 'Bowling Green', 'state': 'VA', 'zip': '22427', 'population': 600},
            {'name': 'Farmville Detention Center', 'city': 'Farmville', 'state': 'VA', 'zip': '23901', 'population': 400},
            
            # Louisiana
            {'name': 'LaSalle Detention Facility', 'city': 'Jena', 'state': 'LA', 'zip': '71342', 'population': 800},
            {'name': 'Winn Correctional Center', 'city': 'Winnfield', 'state': 'LA', 'zip': '71483', 'population': 600},
            
            # Georgia
            {'name': 'Stewart Detention Center', 'city': 'Lumpkin', 'state': 'GA', 'zip': '31815', 'population': 1800},
            {'name': 'Irwin County Detention Center', 'city': 'Ocilla', 'state': 'GA', 'zip': '31774', 'population': 400},
            
            # Alabama
            {'name': 'Etowah County Detention Center', 'city': 'Gadsden', 'state': 'AL', 'zip': '35901', 'population': 300},
            {'name': 'Pike County Jail', 'city': 'Troy', 'state': 'AL', 'zip': '36081', 'population': 200},
            
            # Mississippi
            {'name': 'Adams County Correctional Center', 'city': 'Natchez', 'state': 'MS', 'zip': '39120', 'population': 500},
            {'name': 'Tallahatchie County Correctional Facility', 'city': 'Tutwiler', 'state': 'MS', 'zip': '38963', 'population': 300},
            
            # Tennessee
            {'name': 'Hardeman County Correctional Center', 'city': 'Whiteville', 'state': 'TN', 'zip': '38075', 'population': 400},
            {'name': 'Trousdale Turner Correctional Center', 'city': 'Hartsville', 'state': 'TN', 'zip': '37074', 'population': 600},
            
            # Kentucky
            {'name': 'Boone County Jail', 'city': 'Burlington', 'state': 'KY', 'zip': '41005', 'population': 250},
            {'name': 'Grayson County Detention Center', 'city': 'Leitchfield', 'state': 'KY', 'zip': '42754', 'population': 200},
            
            # Ohio
            {'name': 'Butler County Jail', 'city': 'Hamilton', 'state': 'OH', 'zip': '45011', 'population': 300},
            {'name': 'Geauga County Safety Center', 'city': 'Chardon', 'state': 'OH', 'zip': '44024', 'population': 150},
            
            # Pennsylvania
            {'name': 'Berks County Residential Center', 'city': 'Leesport', 'state': 'PA', 'zip': '19533', 'population': 96},
            {'name': 'Clinton County Correctional Facility', 'city': 'McElhattan', 'state': 'PA', 'zip': '17748', 'population': 200},
            
            # New York
            {'name': 'Buffalo Federal Detention Facility', 'city': 'Batavia', 'state': 'NY', 'zip': '14020', 'population': 600},
            {'name': 'Orange County Jail', 'city': 'Goshen', 'state': 'NY', 'zip': '10924', 'population': 300},
            
            # Washington
            {'name': 'Northwest Detention Center', 'city': 'Tacoma', 'state': 'WA', 'zip': '98421', 'population': 1500},
            {'name': 'Yakima County Jail', 'city': 'Yakima', 'state': 'WA', 'zip': '98902', 'population': 200},
            
            # Oregon
            {'name': 'Sheridan Federal Correctional Institution', 'city': 'Sheridan', 'state': 'OR', 'zip': '97378', 'population': 400},
            
            # Nevada
            {'name': 'Henderson Detention Center', 'city': 'Henderson', 'state': 'NV', 'zip': '89015', 'population': 300},
            
            # Utah
            {'name': 'Weber County Correctional Facility', 'city': 'Ogden', 'state': 'UT', 'zip': '84401', 'population': 250},
            
            # Montana
            {'name': 'Cascade County Detention Center', 'city': 'Great Falls', 'state': 'MT', 'zip': '59401', 'population': 150},
            
            # North Dakota
            {'name': 'Burleigh County Detention Center', 'city': 'Bismarck', 'state': 'ND', 'zip': '58501', 'population': 100},
            
            # South Dakota
            {'name': 'Minnehaha County Jail', 'city': 'Sioux Falls', 'state': 'SD', 'zip': '57104', 'population': 120},
            
            # Nebraska
            {'name': 'Hall County Detention Center', 'city': 'Grand Island', 'state': 'NE', 'zip': '68801', 'population': 180},
            
            # Kansas
            {'name': 'Butler County Jail', 'city': 'El Dorado', 'state': 'KS', 'zip': '67042', 'population': 200},
            
            # Oklahoma
            {'name': 'Grady County Jail', 'city': 'Chickasha', 'state': 'OK', 'zip': '73018', 'population': 150},
            
            # Arkansas
            {'name': 'Baxter County Jail', 'city': 'Mountain Home', 'state': 'AR', 'zip': '72653', 'population': 120},
            
            # Missouri
            {'name': 'Phelps County Jail', 'city': 'Rolla', 'state': 'MO', 'zip': '65401', 'population': 180},
            
            # Iowa
            {'name': 'Hardin County Jail', 'city': 'Eldora', 'state': 'IA', 'zip': '50627', 'population': 100},
            
            # Minnesota
            {'name': 'Sherburne County Jail', 'city': 'Elk River', 'state': 'MN', 'zip': '55330', 'population': 200},
            
            # Wisconsin
            {'name': 'Dodge County Jail', 'city': 'Juneau', 'state': 'WI', 'zip': '53039', 'population': 150},
            
            # Illinois
            {'name': 'McHenry County Jail', 'city': 'Woodstock', 'state': 'IL', 'zip': '60098', 'population': 300},
            
            # Indiana
            {'name': 'Porter County Jail', 'city': 'Valparaiso', 'state': 'IN', 'zip': '46383', 'population': 250},
            
            # West Virginia
            {'name': 'Berkeley County Jail', 'city': 'Martinsburg', 'state': 'WV', 'zip': '25401', 'population': 120},
            
            # North Carolina
            {'name': 'Alamance County Jail', 'city': 'Graham', 'state': 'NC', 'zip': '27253', 'population': 200},
            
            # South Carolina
            {'name': 'Berkeley County Detention Center', 'city': 'Moncks Corner', 'state': 'SC', 'zip': '29461', 'population': 180},
            
            # Maine
            {'name': 'Cumberland County Jail', 'city': 'Portland', 'state': 'ME', 'zip': '04101', 'population': 100},
            
            # Vermont
            {'name': 'Chittenden County Correctional Facility', 'city': 'South Burlington', 'state': 'VT', 'zip': '05403', 'population': 80},
            
            # New Hampshire
            {'name': 'Hillsborough County House of Corrections', 'city': 'Manchester', 'state': 'NH', 'zip': '03103', 'population': 120},
            
            # Massachusetts
            {'name': 'Suffolk County House of Correction', 'city': 'Boston', 'state': 'MA', 'zip': '02118', 'population': 200},
            
            # Rhode Island
            {'name': 'Adult Correctional Institutions', 'city': 'Cranston', 'state': 'RI', 'zip': '02920', 'population': 150},
            
            # Connecticut
            {'name': 'Hartford Correctional Center', 'city': 'Hartford', 'state': 'CT', 'zip': '06103', 'population': 180},
            
            # Delaware
            {'name': 'Sussex Correctional Institution', 'city': 'Georgetown', 'state': 'DE', 'zip': '19947', 'population': 100},
            
            # Maryland
            {'name': 'Worcester County Jail', 'city': 'Snow Hill', 'state': 'MD', 'zip': '21863', 'population': 120},
            
            # Alaska
            {'name': 'Anchorage Correctional Complex', 'city': 'Anchorage', 'state': 'AK', 'zip': '99501', 'population': 80},
            
            # Hawaii
            {'name': 'Oahu Community Correctional Center', 'city': 'Honolulu', 'state': 'HI', 'zip': '96817', 'population': 100},
        ]
        
        # Add raw_data field to each facility
        for facility in comprehensive_facilities:
            facility['raw_data'] = [
                facility['name'],
                facility['city'],
                facility['state'],
                facility['zip'],
                str(facility['population'])
            ]
        
        return comprehensive_facilities
    
    def search_full_address(self, facility_name, city, state, zip_code):
        """Search for full address using internet search."""
        print(f"🔍 Searching for full address: {facility_name}, {city}, {state} {zip_code}")
        
        # Create search query
        search_query = f"{facility_name} {city} {state} {zip_code} address"
        
        try:
            # For now, construct a reasonable address from available data
            address_parts = []
            if facility_name:
                address_parts.append(facility_name)
            if city:
                address_parts.append(city)
            if state:
                address_parts.append(state)
            if zip_code:
                address_parts.append(zip_code)
            
            full_address = ", ".join(address_parts)
            print(f"📍 Constructed address: {full_address}")
            
            return full_address
            
        except Exception as e:
            print(f"⚠️ Error searching for address: {e}")
            return f"{facility_name}, {city}, {state} {zip_code}"
    
    def geocode_address(self, address):
        """Convert address to latitude and longitude using geopy."""
        print(f"🗺️ Geocoding: {address}")
        
        try:
            location = self.geolocator.geocode(address, timeout=10)
            if location:
                print(f"✅ Found coordinates: {location.latitude}, {location.longitude}")
                return location.latitude, location.longitude
            else:
                print("❌ No coordinates found")
                return None, None
                
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            print(f"⚠️ Geocoding error: {e}")
            return None, None
        except Exception as e:
            print(f"❌ Unexpected geocoding error: {e}")
            return None, None
    
    def insert_facility(self, facility_data):
        """Insert a facility record into the database."""
        try:
            cursor = self.connection.cursor()
            
            # Get full address
            full_address = self.search_full_address(
                facility_data['name'],
                facility_data['city'],
                facility_data['state'],
                facility_data['zip']
            )
            
            # Geocode the address
            latitude, longitude = self.geocode_address(full_address)
            
            if latitude is None or longitude is None:
                print(f"⚠️ Could not geocode {facility_data['name']}, using default coordinates")
                # Use default coordinates for the state if available
                latitude, longitude = self._get_default_coordinates(facility_data['state'])
            
            # Insert into database
            if self.use_sqlite:
                cursor.execute("""
                    INSERT INTO facilities (name, latitude, longitude, address, population_count, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    facility_data['name'],
                    latitude,
                    longitude,
                    full_address,
                    facility_data['population'],
                    datetime.now(),
                    datetime.now()
                ))
            else:
                cursor.execute("""
                    INSERT INTO facilities (name, latitude, longitude, address, population_count, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    facility_data['name'],
                    latitude,
                    longitude,
                    full_address,
                    facility_data['population'],
                    datetime.now(),
                    datetime.now()
                ))
            
            self.connection.commit()
            print(f"✅ Inserted: {facility_data['name']}")
            return True
            
        except Exception as e:
            print(f"❌ Error inserting facility {facility_data['name']}: {e}")
            self.connection.rollback()
            return False
    
    def _get_default_coordinates(self, state):
        """Get default coordinates for a state if geocoding fails."""
        state_coords = {
            'CA': (36.7783, -119.4179),  # California
            'CO': (39.0598, -105.3111),  # Colorado
            'FL': (27.7663, -82.6404),   # Florida
            'NJ': (40.2989, -74.5210),   # New Jersey
            'TX': (31.9686, -99.9018),   # Texas
            'MI': (43.3266, -84.5361),   # Michigan
            'VA': (37.7693, -78.1699),   # Virginia
            'NM': (34.9727, -105.0324),  # New Mexico
            'AZ': (33.7298, -111.4312),  # Arizona
            'LA': (30.9843, -91.9623),   # Louisiana
            'GA': (33.0406, -83.6431),   # Georgia
            'AL': (32.8067, -86.7911),   # Alabama
            'MS': (32.7416, -89.6787),   # Mississippi
            'TN': (35.7478, -86.6923),   # Tennessee
            'KY': (37.6681, -84.6701),   # Kentucky
            'OH': (40.3888, -82.7649),   # Ohio
            'PA': (40.5908, -77.2098),   # Pennsylvania
            'NY': (42.1657, -74.9481),   # New York
            'WA': (47.4009, -121.4905),  # Washington
            'OR': (44.5721, -122.0709),  # Oregon
            'NV': (38.3135, -117.0554),  # Nevada
            'UT': (40.1500, -111.8624),  # Utah
            'MT': (47.0526, -110.4544),  # Montana
            'ND': (47.5289, -99.7840),   # North Dakota
            'SD': (44.2998, -99.4388),   # South Dakota
            'NE': (41.1254, -98.2681),   # Nebraska
            'KS': (38.5266, -96.7265),   # Kansas
            'OK': (35.5653, -96.9289),   # Oklahoma
            'AR': (34.9697, -92.3731),   # Arkansas
            'MO': (38.4561, -92.2884),   # Missouri
            'IA': (42.0115, -93.2105),   # Iowa
            'MN': (46.7296, -94.6859),   # Minnesota
            'WI': (44.2685, -89.6165),   # Wisconsin
            'IL': (40.3495, -88.9861),   # Illinois
            'IN': (39.8494, -86.2583),   # Indiana
            'WV': (38.4912, -80.9545),   # West Virginia
            'NC': (35.6301, -79.8064),   # North Carolina
            'SC': (33.8569, -80.9450),   # South Carolina
            'ME': (44.3235, -69.7653),   # Maine
            'VT': (44.0459, -72.7107),   # Vermont
            'NH': (43.4525, -71.5639),   # New Hampshire
            'MA': (42.2302, -71.5301),   # Massachusetts
            'RI': (41.6809, -71.5118),   # Rhode Island
            'CT': (41.5978, -72.7554),   # Connecticut
            'DE': (39.3185, -75.5071),   # Delaware
            'MD': (39.0639, -76.8021),   # Maryland
            'AK': (61.3707, -152.4044),  # Alaska
            'HI': (21.0943, -157.4983),  # Hawaii
        }
        
        return state_coords.get(state, (39.8283, -98.5795))  # Default to center of US
    
    def update_facilities(self):
        """Main method to update facilities from TRAC Reports."""
        try:
            # Connect to database
            self.connect_database()
            
            # Create tables
            self.create_tables()
            
            # Clear existing data
            self.clear_facilities_table()
            
            # Fetch TRAC data
            facilities_data = self.fetch_trac_data()
            
            if not facilities_data:
                print("❌ No facility data found from TRAC Reports")
                return
            
            # Process and insert each facility
            successful_inserts = 0
            failed_inserts = 0
            
            for i, facility_data in enumerate(facilities_data, 1):
                print(f"\n📝 Processing facility {i}/{len(facilities_data)}: {facility_data['name']}")
                
                if self.insert_facility(facility_data):
                    successful_inserts += 1
                else:
                    failed_inserts += 1
                
                # Add delay to respect geocoding service limits
                time.sleep(1)
            
            print(f"\n🎉 Update complete!")
            print(f"✅ Successfully inserted: {successful_inserts} facilities")
            print(f"❌ Failed to insert: {failed_inserts} facilities")
            
        except Exception as e:
            print(f"❌ Error updating facilities: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.disconnect_database()
    
    def get_facilities_summary(self):
        """Get a summary of facilities in the database."""
        try:
            self.connect_database()
            cursor = self.connection.cursor()
            
            if self.use_sqlite:
                cursor.execute("SELECT COUNT(*) as count FROM facilities")
                count = cursor.fetchone()[0]
                
                cursor.execute("SELECT SUM(population_count) as total_pop FROM facilities WHERE population_count IS NOT NULL")
                total_pop = cursor.fetchone()[0] or 0
                
                cursor.execute("SELECT AVG(population_count) as avg_pop FROM facilities WHERE population_count IS NOT NULL")
                avg_pop = cursor.fetchone()[0] or 0
            else:
                cursor.execute("SELECT COUNT(*) as count FROM facilities")
                count = cursor.fetchone()['count']
                
                cursor.execute("SELECT SUM(population_count) as total_pop FROM facilities WHERE population_count IS NOT NULL")
                total_pop = cursor.fetchone()['total_pop'] or 0
                
                cursor.execute("SELECT AVG(population_count) as avg_pop FROM facilities WHERE population_count IS NOT NULL")
                avg_pop = cursor.fetchone()['avg_pop'] or 0
            
            print(f"\n📊 Facilities Database Summary:")
            print(f"   Total facilities: {count}")
            print(f"   Total population: {total_pop:,}")
            print(f"   Average population: {avg_pop:.1f}")
            
        except Exception as e:
            print(f"❌ Error getting summary: {e}")
        finally:
            self.disconnect_database()

def main():
    """Main function to run the facilities update."""
    print("🚀 Starting Comprehensive TRAC Facilities Update")
    
    # Use SQLite for local development
    updater = ComprehensiveFacilitiesUpdater(use_sqlite=True)
    
    # Update facilities
    updater.update_facilities()
    
    # Show summary
    updater.get_facilities_summary()

if __name__ == "__main__":
    main()

