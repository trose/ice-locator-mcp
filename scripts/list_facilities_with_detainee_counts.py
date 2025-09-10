"""
Script to list all facilities with their detainee counts from the enriched_detainees.csv file.
"""
import csv
import os
from collections import defaultdict


def list_facilities_with_detainee_counts(csv_file_path: str = None):
    """
    List all facilities with their detainee counts.
    
    Args:
        csv_file_path: Path to the CSV file (defaults to project root enriched_detainees.csv)
    """
    if csv_file_path is None:
        # Default to the enriched_detainees.csv in the project root
        csv_file_path = os.path.join(
            os.path.dirname(__file__),
            'enriched_detainees.csv'
        )
    
    if not os.path.exists(csv_file_path):
        raise FileNotFoundError(f"CSV file not found: {csv_file_path}")
    
    # Dictionary to store detainee counts by facility
    facility_counts = defaultdict(int)
    total_count = 0
    
    # Read CSV and count detainees by facility
    with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            # Extract facility name
            facility_name = row.get('facility_name', '').strip()
            
            # Skip if no facility data
            if not facility_name:
                continue
            
            # Increment count for this facility
            facility_counts[facility_name] += 1
            total_count += 1
    
    # Print results
    print(f"Total detainees: {total_count}")
    print(f"Total facilities: {len(facility_counts)}\n")
    print("Facilities sorted by detainee count (highest first):")
    print("=" * 60)
    
    # Sort by count (descending) then by facility name
    sorted_facilities = sorted(facility_counts.items(), key=lambda x: (-x[1], x[0]))
    
    for facility, count in sorted_facilities:
        print(f"{facility}: {count} detainees")


if __name__ == "__main__":
    list_facilities_with_detainee_counts()