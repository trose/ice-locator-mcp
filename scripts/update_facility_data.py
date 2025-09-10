#!/usr/bin/env python3
"""
Automated facility data updater for GitHub Actions.
Fetches data from TRAC Reports and updates embedded JSON.
"""

import requests
import json
import os
from datetime import datetime
from typing import List, Dict

class FacilityDataUpdater:
    def __init__(self):
        self.trac_url = "https://tracreports.org/immigration/detentionstats/facilities.json"
        self.output_path = "web-app/src/data/facilities.json"
    
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
    
    def process_facility_data(self, raw_data: List[Dict]) -> Dict:
        """Process raw TRAC data into our format."""
        print("🔄 Processing facility data...")
        
        facilities = []
        total_population = 0
        
        for entry in raw_data:
            # Skip total entries and invalid data
            if entry.get('name') == 'Total' or not entry.get('name'):
                continue
            
            # Extract and validate coordinates
            lat = entry.get('latitude', 0)
            lng = entry.get('longitude', 0)
            
            # Skip facilities with invalid coordinates
            if lat == 0 and lng == 0:
                print(f"⚠️  Skipping {entry.get('name')} - invalid coordinates")
                continue
            
            facility = {
                "name": entry.get('name', ''),
                "latitude": float(lat) if lat else 0,
                "longitude": float(lng) if lng else 0,
                "address": entry.get('address', ''),
                "population_count": int(entry.get('current_detainee_count', 0))
            }
            
            facilities.append(facility)
            total_population += facility['population_count']
        
        print(f"📊 Processed {len(facilities)} valid facilities")
        print(f"👥 Total population: {total_population:,}")
        
        return {
            "metadata": {
                "exported_at": datetime.now().isoformat(),
                "total_facilities": len(facilities),
                "total_population": total_population,
                "description": "ICE Detention Facilities - Population Data",
                "source": "TRAC Reports",
                "source_url": self.trac_url,
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
            },
            "facilities": facilities
        }
    
    def update_facilities_file(self, data: Dict):
        """Update the facilities JSON file."""
        print(f"💾 Writing data to {self.output_path}")
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        
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
