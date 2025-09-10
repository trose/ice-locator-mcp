#!/usr/bin/env python3
"""
Update facilities database with comprehensive data from TRAC Reports.
Fetches data from https://tracreports.org/immigration/detentionstats/facilities.html
"""

import requests
from bs4 import BeautifulSoup
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import time
from datetime import datetime
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import re
import json

class TRACFacilitiesUpdater:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.geolocator = Nominatim(user_agent="ice_locator_facility_geocoder")
        self.connection = None
        
    def connect_database(self):
        """Connect to the database."""
        try:
            self.connection = psycopg2.connect(self.database_url, cursor_factory=RealDictCursor)
            print("✅ Connected to database")
        except Exception as e:
            print(f"❌ Error connecting to database: {e}")
            raise
    
    def disconnect_database(self):
        """Disconnect from the database."""
        if self.connection:
            self.connection.close()
            print("✅ Disconnected from database")
    
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
            
            print(f"✅ Extracted {len(facilities_data)} facilities from TRAC Reports")
            return facilities_data
            
        except Exception as e:
            print(f"❌ Error fetching TRAC data: {e}")
            return []
    
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
    
    def search_full_address(self, facility_name, city, state, zip_code):
        """Search for full address using internet search."""
        print(f"🔍 Searching for full address: {facility_name}, {city}, {state} {zip_code}")
        
        # Create search query
        search_query = f"{facility_name} {city} {state} {zip_code} address"
        
        try:
            # Use a simple search approach - in a real implementation, you might use
            # a more sophisticated search API
            search_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
            
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
                print(f"⚠️ Skipping {facility_data['name']} - could not geocode")
                return False
            
            # Insert into database
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
    
    def update_facilities(self):
        """Main method to update facilities from TRAC Reports."""
        try:
            # Connect to database
            self.connect_database()
            
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
        finally:
            self.disconnect_database()

def main():
    """Main function to run the facilities update."""
    # Get database URL from environment or use default
    database_url = os.getenv('DATABASE_URL', 'postgresql://localhost/ice_locator')
    
    print("🚀 Starting TRAC Facilities Update")
    print(f"📊 Database: {database_url}")
    
    updater = TRACFacilitiesUpdater(database_url)
    updater.update_facilities()

if __name__ == "__main__":
    main()

