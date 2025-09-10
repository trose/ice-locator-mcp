#!/usr/bin/env python3
"""
Automated facility data updater for GitHub Actions.
Fetches data from TRAC Reports and updates embedded JSON.
"""

import requests
import json
import os
import time
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

class FacilityDataUpdater:
    def __init__(self):
        self.trac_url = "https://tracreports.org/immigration/detentionstats/facilities.json"
        self.output_path = "web-app/src/data/facilities.json"
        # Initialize geocoder with a user agent
        self.geocoder = Nominatim(user_agent="ice-facility-heatmap/1.0")
        # Cache for geocoding results to avoid repeated API calls
        self.geocoding_cache = {}
    
    def fetch_trac_data(self) -> List[Dict]:
        """Fetch latest data from TRAC Reports."""
        try:
            print(f"🌐 Fetching data from {self.trac_url}")
            response = requests.get(self.trac_url, timeout=30)
            response.raise_for_status()
            data = response.json()
            print(f"✅ Successfully fetched {len(data)} records")
            return data
        except Exception as e:
            print(f"❌ Error fetching TRAC data: {e}")
            raise
    
    def geocode_facility(self, facility_name: str, city: str, state: str, zip_code: str = "") -> Optional[Tuple[float, float]]:
        """Geocode a facility address to get coordinates."""
        # Create a cache key
        cache_key = f"{facility_name}, {city}, {state}, {zip_code}".strip(", ")
        
        # Check cache first
        if cache_key in self.geocoding_cache:
            return self.geocoding_cache[cache_key]
        
        # Try multiple address formats for better success rate
        address_formats = [
            f"{facility_name}, {city}, {state}, {zip_code}".strip(", "),
            f"{facility_name}, {city}, {state}".strip(", "),
            f"{city}, {state}, {zip_code}".strip(", "),
            f"{city}, {state}".strip(", ")
        ]
        
        for address in address_formats:
            if not address or address == ", ":
                continue
                
            try:
                print(f"🗺️  Geocoding: {address}")
                
                # Geocode with timeout
                location = self.geocoder.geocode(address, timeout=10)
                
                if location:
                    coords = (location.latitude, location.longitude)
                    self.geocoding_cache[cache_key] = coords
                    print(f"✅ Found coordinates: {coords[0]:.4f}, {coords[1]:.4f}")
                    return coords
                    
            except (GeocoderTimedOut, GeocoderServiceError) as e:
                print(f"⚠️  Geocoding error for {address}: {e}")
                continue
            except Exception as e:
                print(f"❌ Unexpected geocoding error for {address}: {e}")
                continue
        
        print(f"⚠️  No coordinates found for any address format")
        self.geocoding_cache[cache_key] = None
        return None
    
    def process_facility_data(self, raw_data: List[Dict]) -> Dict:
        """Process raw TRAC data into our format."""
        print("🔄 Processing facility data...")
        
        facilities = []
        total_population = 0
        geocoded_count = 0
        skipped_count = 0
        
        # Filter out staging facilities and focus on actual detention centers
        detention_types = {'CDF', 'SPC', 'DIGSA', 'IGSA', 'BOP', 'FAMILY'}
        
        for i, entry in enumerate(raw_data):
            # Skip total entries and invalid data
            if entry.get('name') == 'Total' or not entry.get('name'):
                continue
            
            # Skip staging facilities and other non-detention types
            facility_type = entry.get('type_detailed', '')
            if facility_type not in detention_types:
                continue
            
            # Extract facility information
            name = entry.get('name', '').strip()
            city = entry.get('detention_facility_city', '').strip()
            state = entry.get('detention_facility_state', '').strip()
            zip_code = entry.get('detention_facility_zip', '').strip()
            
            # Parse population count
            count_str = entry.get('count', '0').strip()
            # Remove commas and convert to int
            try:
                population_count = int(count_str.replace(',', '').replace(' ', ''))
            except (ValueError, AttributeError):
                population_count = 0
            
            # Skip facilities with no population
            if population_count <= 0:
                continue
            
            # Geocode the facility
            coords = self.geocode_facility(name, city, state, zip_code)
            
            if coords:
                lat, lng = coords
                
                # Build address string
                address_parts = [city, state, zip_code]
                address = ", ".join(filter(None, address_parts))
                
                facility = {
                    "name": name,
                    "latitude": lat,
                    "longitude": lng,
                    "address": address,
                    "population_count": population_count,
                    "facility_type": facility_type
                }
                
                facilities.append(facility)
                total_population += population_count
                geocoded_count += 1
                
                print(f"✅ {geocoded_count}: {name} - {population_count:,} detainees")
            else:
                skipped_count += 1
                print(f"⚠️  Skipped {name} - could not geocode")
            
            # Add delay to respect geocoding service rate limits
            if i % 10 == 0 and i > 0:
                print(f"⏸️  Pausing for rate limiting... ({i}/{len(raw_data)} processed)")
                time.sleep(1)
        
        print(f"\n📊 Processing complete!")
        print(f"✅ Successfully geocoded: {geocoded_count} facilities")
        print(f"⚠️  Skipped (no coordinates): {skipped_count} facilities")
        print(f"👥 Total population: {total_population:,}")
        
        return {
            "metadata": {
                "exported_at": datetime.now().isoformat(),
                "total_facilities": len(facilities),
                "total_population": total_population,
                "description": "ICE Detention Facilities - Population Data",
                "source": "TRAC Reports",
                "source_url": self.trac_url,
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
                "geocoded_facilities": geocoded_count,
                "skipped_facilities": skipped_count
            },
            "facilities": facilities
        }
    
    def update_facilities_file(self, data: Dict):
        """Update the facilities JSON file."""
        print(f"💾 Writing data to {self.output_path}")
        
        # Ensure directory exists
        output_dir = os.path.dirname(self.output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Write formatted JSON
        with open(self.output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Updated {self.output_path}")
        print(f"📈 Total facilities: {data['metadata']['total_facilities']}")
        print(f"👥 Total population: {data['metadata']['total_population']:,}")
    
    def validate_data(self, data: Dict) -> bool:
        """Validate the processed data."""
        print("🔍 Validating data...")
        
        metadata = data.get('metadata', {})
        facilities = data.get('facilities', [])
        
        # Check metadata
        if not metadata.get('total_facilities'):
            print("❌ Missing total_facilities in metadata")
            return False
        
        if not metadata.get('total_population'):
            print("❌ Missing total_population in metadata")
            return False
        
        # Check facilities
        if len(facilities) == 0:
            print("❌ No facilities found")
            return False
        
        # Check for reasonable data ranges
        if metadata['total_facilities'] < 100:
            print(f"⚠️  Low facility count: {metadata['total_facilities']}")
        
        if metadata['total_population'] < 10000:
            print(f"⚠️  Low population count: {metadata['total_population']}")
        
        print("✅ Data validation passed")
        return True
    
    def run(self):
        """Main execution method."""
        print("🚀 Starting facility data update...")
        print(f"📅 Timestamp: {datetime.now().isoformat()}")
        
        try:
            # Fetch data
            raw_data = self.fetch_trac_data()
            
            # Process data
            processed_data = self.process_facility_data(raw_data)
            
            # Validate data
            if not self.validate_data(processed_data):
                print("❌ Data validation failed")
                return False
            
            # Update file
            self.update_facilities_file(processed_data)
            
            print("🎉 Facility data update complete!")
            return True
            
        except Exception as e:
            print(f"💥 Update failed: {e}")
            return False

if __name__ == "__main__":
    updater = FacilityDataUpdater()
    success = updater.run()
    exit(0 if success else 1)
