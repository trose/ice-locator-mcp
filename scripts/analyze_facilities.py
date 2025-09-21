#!/usr/bin/env python3
import json
import sys
from pathlib import Path

def analyze_facilities():
    """Analyze facilities data and identify top facilities by population"""

    # Load the comprehensive facilities data
    facilities_file = Path("/Users/trose/src/ice-locator-mcp/data/facilities/comprehensive_ice_facilities.json")

    if not facilities_file.exists():
        print(f"Error: {facilities_file} not found")
        sys.exit(1)

    with open(facilities_file, 'r') as f:
        facilities = json.load(f)

    print(f"Total facilities loaded: {len(facilities)}")

    # Sort facilities by population (descending)
    sorted_facilities = sorted(facilities, key=lambda x: x.get('population', 0), reverse=True)

    # Get top 30 facilities
    top_facilities = sorted_facilities[:30]

    print("\nTop 30 ICE Facilities by Population:")
    print("=" * 60)

    for i, facility in enumerate(top_facilities, 1):
        name = facility.get('name', 'Unknown')
        city = facility.get('city', 'Unknown')
        state = facility.get('state', 'Unknown')
        population = facility.get('population', 0)

        print(f"{i:2d}. {name}")
        print(f"    Location: {city}, {state}")
        print(f"    Population: {population:,}")
        print()

    # Save top facilities to a separate file for easy reference
    output_file = Path("/Users/trose/src/ice-locator-mcp/data/facilities/top_30_facilities.json")
    with open(output_file, 'w') as f:
        json.dump(top_facilities, f, indent=2)

    print(f"Top 30 facilities saved to: {output_file}")

    # Also create a summary with basic stats
    total_population = sum(f.get('population', 0) for f in facilities)
    avg_population = total_population / len(facilities) if facilities else 0

    print("\nSummary Statistics:")
    print(f"Total facilities: {len(facilities)}")
    print(f"Total population across all facilities: {total_population:,}")
    print(f"Average population per facility: {avg_population:.1f}")
    print(f"Top facility population: {top_facilities[0]['population']:,}")
    print(f"Smallest facility population: {sorted_facilities[-1]['population']:,}")

if __name__ == "__main__":
    analyze_facilities()