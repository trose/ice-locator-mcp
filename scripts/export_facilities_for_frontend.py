#!/usr/bin/env python3
"""
Export facilities data for frontend embedding.
Creates a minimal JSON file with only the data needed for the heatmap.
"""

import json
import sqlite3
from datetime import datetime

def export_facilities_data():
    """Export facilities data to a minimal JSON format for frontend embedding."""
    print("📊 Exporting facilities data for frontend embedding...")
    
    # Connect to SQLite database
    conn = sqlite3.connect('ice_locator_facilities.db')
    cursor = conn.cursor()
    
    # Get all facilities with only the fields we need
    cursor.execute("""
        SELECT name, latitude, longitude, address, population_count
        FROM facilities
        WHERE population_count IS NOT NULL AND population_count > 0
        ORDER BY population_count DESC
    """)
    
    facilities = []
    for row in cursor.fetchall():
        name, lat, lng, address, population = row
        facilities.append({
            "name": name,
            "latitude": lat,
            "longitude": lng,
            "address": address or "",
            "population_count": population
        })
    
    conn.close()
    
    # Create the data structure for frontend
    frontend_data = {
        "metadata": {
            "exported_at": datetime.now().isoformat(),
            "total_facilities": len(facilities),
            "total_population": sum(f["population_count"] for f in facilities),
            "description": "ICE Detention Facilities - Population Data"
        },
        "facilities": facilities
    }
    
    # Save to JSON file
    output_file = "web-app/src/data/facilities.json"
    with open(output_file, 'w') as f:
        json.dump(frontend_data, f, indent=2)
    
    print(f"✅ Exported {len(facilities)} facilities to {output_file}")
    print(f"📊 Total population: {frontend_data['metadata']['total_population']:,}")
    
    # Also create a CSV for backup
    csv_file = "web-app/public/facilities.csv"
    with open(csv_file, 'w') as f:
        f.write("name,latitude,longitude,address,population_count\n")
        for facility in facilities:
            f.write(f'"{facility["name"]}",{facility["latitude"]},{facility["longitude"]},"{facility["address"]}",{facility["population_count"]}\n')
    
    print(f"📄 Also created CSV backup at {csv_file}")
    
    return frontend_data

if __name__ == "__main__":
    export_facilities_data()

