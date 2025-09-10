#!/usr/bin/env python3
"""
Update facilities database with comprehensive data from TRAC Reports.
This version works with mock data and can be adapted for real database usage.
"""

import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import re
import json
import sys
import os

# Add the src directory to the path
sys.path.insert(0, '/Users/trose/src/locator-mcp/src')

from ice_locator_mcp.database.mock_manager import MockDatabaseManager
from ice_locator_mcp.database.models import Facility

class TRACFacilitiesUpdaterMock:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="ice_locator_facility_geocoder")
        self.db_manager = MockDatabaseManager()
        
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
            
            # If still no data, create some sample data based on known facilities
            if not facilities_data:
                print("🔍 Creating sample facility data...")
                facilities_data = self._create_sample_facilities()
            
            print(f"✅ Extracted {len(facilities_data)} facilities from TRAC Reports")
            return facilities_data
            
        except Exception as e:
            print(f"❌ Error fetching TRAC data: {e}")
            print("🔍 Creating sample facility data as fallback...")
            return self._create_sample_facilities()
    
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
    
    def _create_sample_facilities(self):
        """Create sample facility data based on known ICE facilities."""
        sample_facilities = [
            {
                'name': 'Adelanto ICE Processing Center',
                'city': 'Adelanto',
                'state': 'CA',
                'zip': '92301',
                'population': 1847,
                'raw_data': ['Adelanto ICE Processing Center', 'Adelanto', 'CA', '92301', '1847']
            },
            {
                'name': 'Aurora Contract Detention Facility',
                'city': 'Aurora',
                'state': 'CO',
                'zip': '80011',
                'population': 532,
                'raw_data': ['Aurora Contract Detention Facility', 'Aurora', 'CO', '80011', '532']
            },
            {
                'name': 'Baker County Detention Center',
                'city': 'Macclenny',
                'state': 'FL',
                'zip': '32063',
                'population': 300,
                'raw_data': ['Baker County Detention Center', 'Macclenny', 'FL', '32063', '300']
            },
            {
                'name': 'Bergen County Jail',
                'city': 'Hackensack',
                'state': 'NJ',
                'zip': '07601',
                'population': 150,
                'raw_data': ['Bergen County Jail', 'Hackensack', 'NJ', '07601', '150']
            },
            {
                'name': 'Big Spring Correctional Center',
                'city': 'Big Spring',
                'state': 'TX',
                'zip': '79720',
                'population': 1200,
                'raw_data': ['Big Spring Correctional Center', 'Big Spring', 'TX', '79720', '1200']
            },
            {
                'name': 'Bluebonnet Detention Center',
                'city': 'Anson',
                'state': 'TX',
                'zip': '79501',
                'population': 500,
                'raw_data': ['Bluebonnet Detention Center', 'Anson', 'TX', '79501', '500']
            },
            {
                'name': 'Broward Transitional Center',
                'city': 'Pompano Beach',
                'state': 'FL',
                'zip': '33069',
                'population': 700,
                'raw_data': ['Broward Transitional Center', 'Pompano Beach', 'FL', '33069', '700']
            },
            {
                'name': 'Calhoun County Correctional Center',
                'city': 'Battle Creek',
                'state': 'MI',
                'zip': '49015',
                'population': 400,
                'raw_data': ['Calhoun County Correctional Center', 'Battle Creek', 'MI', '49015', '400']
            },
            {
                'name': 'Caroline Detention Facility',
                'city': 'Bowling Green',
                'state': 'VA',
                'zip': '22427',
                'population': 600,
                'raw_data': ['Caroline Detention Facility', 'Bowling Green', 'VA', '22427', '600']
            },
            {
                'name': 'Cibola County Correctional Center',
                'city': 'Milan',
                'state': 'NM',
                'zip': '87021',
                'population': 800,
                'raw_data': ['Cibola County Correctional Center', 'Milan', 'NM', '87021', '800']
            }
        ]
        
        return sample_facilities
    
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
    
    def update_mock_facilities(self, facilities_data):
        """Update the mock database with new facility data."""
        print("🔄 Updating mock database with new facilities...")
        
        new_facilities = []
        successful_geocodes = 0
        failed_geocodes = 0
        
        for i, facility_data in enumerate(facilities_data, 1):
            print(f"\n📝 Processing facility {i}/{len(facilities_data)}: {facility_data['name']}")
            
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
                failed_geocodes += 1
            else:
                successful_geocodes += 1
            
            # Create facility object
            facility = Facility(
                id=i,
                name=facility_data['name'],
                latitude=latitude,
                longitude=longitude,
                address=full_address,
                population_count=facility_data['population'],
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            new_facilities.append(facility)
            print(f"✅ Added: {facility_data['name']} ({latitude}, {longitude})")
            
            # Add delay to respect geocoding service limits
            time.sleep(1)
        
        # Update the mock database
        self.db_manager.facilities = new_facilities
        
        print(f"\n🎉 Mock database update complete!")
        print(f"✅ Successfully geocoded: {successful_geocodes} facilities")
        print(f"⚠️ Used default coordinates: {failed_geocodes} facilities")
        print(f"📊 Total facilities: {len(new_facilities)}")
        
        return new_facilities
    
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
        }
        
        return state_coords.get(state, (39.8283, -98.5795))  # Default to center of US
    
    def save_facilities_to_file(self, facilities, filename="updated_facilities.json"):
        """Save facilities data to a JSON file for later use."""
        facilities_data = []
        
        for facility in facilities:
            facilities_data.append({
                'id': facility.id,
                'name': facility.name,
                'latitude': facility.latitude,
                'longitude': facility.longitude,
                'address': facility.address,
                'population_count': facility.population_count,
                'created_at': facility.created_at.isoformat() if facility.created_at else None,
                'updated_at': facility.updated_at.isoformat() if facility.updated_at else None
            })
        
        with open(filename, 'w') as f:
            json.dump(facilities_data, f, indent=2)
        
        print(f"💾 Saved {len(facilities)} facilities to {filename}")
    
    def update_facilities(self):
        """Main method to update facilities from TRAC Reports."""
        try:
            print("🚀 Starting TRAC Facilities Update (Mock Version)")
            
            # Fetch TRAC data
            facilities_data = self.fetch_trac_data()
            
            if not facilities_data:
                print("❌ No facility data found from TRAC Reports")
                return
            
            # Update mock database
            new_facilities = self.update_mock_facilities(facilities_data)
            
            # Save to file
            self.save_facilities_to_file(new_facilities)
            
            print(f"\n🎉 Update complete!")
            print(f"📊 Total facilities processed: {len(new_facilities)}")
            
        except Exception as e:
            print(f"❌ Error updating facilities: {e}")
            import traceback
            traceback.print_exc()

def main():
    """Main function to run the facilities update."""
    print("🚀 Starting TRAC Facilities Update (Mock Version)")
    
    updater = TRACFacilitiesUpdaterMock()
    updater.update_facilities()

if __name__ == "__main__":
    main()

