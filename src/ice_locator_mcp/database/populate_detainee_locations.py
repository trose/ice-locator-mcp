"""
Script to populate detainee locations from enriched_detainees.csv.
"""
import csv
import os
from datetime import datetime
from .models import Detainee
from .manager import DatabaseManager


def populate_detainee_locations(database_url: str, csv_file_path: str = None):
    """
    Populate detainee locations from CSV file.
    
    Args:
        database_url: PostgreSQL connection string
        csv_file_path: Path to the CSV file (defaults to project root enriched_detainees.csv)
    """
    if csv_file_path is None:
        # Default to the enriched_detainees.csv in the project root
        csv_file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            'enriched_detainees.csv'
        )
    
    if not os.path.exists(csv_file_path):
        raise FileNotFoundError(f"CSV file not found: {csv_file_path}")
    
    # Initialize database manager
    db_manager = DatabaseManager(database_url)
    db_manager.connect()
    
    try:
        # Create tables if they don't exist
        db_manager.create_tables()
        
        # Read CSV and populate detainees
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            processed_count = 0
            
            for row in reader:
                # Extract first and last name (assuming they exist in the CSV)
                first_name = row.get('first_name', '').strip()
                last_name = row.get('last_name', '').strip()
                
                # Skip if no name data
                if not first_name and not last_name:
                    continue
                
                # Create detainee object
                detainee = Detainee(
                    id=None,
                    first_name=first_name,
                    last_name=last_name,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                
                # Insert into database
                try:
                    db_manager.insert_detainee(detainee)
                    processed_count += 1
                except Exception as e:
                    print(f"Error inserting detainee {first_name} {last_name}: {e}")
                    continue
            
            print(f"Successfully processed {processed_count} detainees from {csv_file_path}")
            
    finally:
        db_manager.disconnect()


if __name__ == "__main__":
    # This would normally be configured through environment variables
    DATABASE_URL = "postgresql://localhost/ice_locator"
    populate_detainee_locations(DATABASE_URL)