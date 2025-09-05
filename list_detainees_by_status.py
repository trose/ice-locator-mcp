"""
Script to list all detainees by custody status from the enriched_detainees.csv file.
"""
import csv
import os
from collections import defaultdict


def list_detainees_by_status(csv_file_path: str = None):
    """
    List all detainees grouped by custody status.
    
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
    
    # Dictionary to store detainees by status
    status_groups = defaultdict(list)
    total_count = 0
    
    # Read CSV and group detainees by status
    with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            # Extract relevant information
            first_name = row.get('first_name', '').strip()
            last_name = row.get('last_name', '').strip()
            custody_status = row.get('custody_status', '').strip()
            
            # Skip if no status data
            if not custody_status:
                continue
            
            # Add detainee to the appropriate group
            full_name = f"{first_name} {last_name}".strip()
            status_groups[custody_status].append(full_name)
            total_count += 1
    
    # Print results
    print(f"Total detainees: {total_count}\n")
    print("Detainees by custody status:")
    print("=" * 50)
    
    # Sort by status name for consistent output
    for status in sorted(status_groups.keys()):
        detainees = status_groups[status]
        print(f"\n{status}: {len(detainees)} detainees")
        # Print first 10 detainees as examples
        for detainee in sorted(detainees)[:10]:
            print(f"  - {detainee}")
        if len(detainees) > 10:
            print(f"  ... and {len(detainees) - 10} more")


if __name__ == "__main__":
    list_detainees_by_status()