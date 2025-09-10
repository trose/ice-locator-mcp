#!/usr/bin/env python3
"""
Examine TRAC Reports data structure to understand the API response format.
"""

import requests
import json

def examine_trac_data():
    """Examine the TRAC Reports data structure."""
    print("🔍 Examining TRAC Reports data structure...")
    
    try:
        response = requests.get("https://tracreports.org/immigration/detentionstats/facilities.json", timeout=30)
        response.raise_for_status()
        data = response.json()
        
        print(f"📊 Total records: {len(data)}")
        print(f"📅 Response status: {response.status_code}")
        
        # Show first few records
        print("\n📋 First 5 records:")
        for i, record in enumerate(data[:5]):
            print(f"\n{i+1}. {record.get('name', 'NO_NAME')}")
            print(f"   Count: {record.get('count', 'NO_COUNT')}")
            print(f"   Type: {record.get('type_detailed', 'NO_TYPE')}")
            print(f"   City: {record.get('detention_facility_city', 'NO_CITY')}")
            print(f"   State: {record.get('detention_facility_state', 'NO_STATE')}")
            print(f"   Date: {record.get('download_date', 'NO_DATE')}")
        
        # Look for records with actual facility names (not "Total")
        print("\n🏢 Sample facility records (non-Total):")
        facility_count = 0
        for record in data:
            if record.get('name') != 'Total' and record.get('name'):
                print(f"\n{facility_count+1}. {record.get('name')}")
                print(f"   Count: {record.get('count', 'NO_COUNT')}")
                print(f"   Type: {record.get('type_detailed', 'NO_TYPE')}")
                print(f"   City: {record.get('detention_facility_city', 'NO_CITY')}")
                print(f"   State: {record.get('detention_facility_state', 'NO_STATE')}")
                print(f"   Date: {record.get('download_date', 'NO_DATE')}")
                facility_count += 1
                if facility_count >= 5:
                    break
        
        # Check for coordinate fields
        print("\n🗺️  Checking for coordinate fields...")
        sample_record = data[1] if len(data) > 1 else data[0]
        print("Available fields in sample record:")
        for key, value in sample_record.items():
            print(f"   {key}: {value}")
        
        # Count records by type
        print("\n📈 Records by type:")
        type_counts = {}
        for record in data:
            record_type = record.get('type_detailed', 'UNKNOWN')
            type_counts[record_type] = type_counts.get(record_type, 0) + 1
        
        for record_type, count in sorted(type_counts.items()):
            print(f"   {record_type}: {count}")
        
    except Exception as e:
        print(f"❌ Error examining data: {e}")

if __name__ == "__main__":
    examine_trac_data()
