#!/usr/bin/env python3
"""
Optimized Monthly Data Structure Generator
Creates a more efficient JSON structure for frontend embedding by:
1. Separating facility metadata from monthly data
2. Using arrays instead of objects for monthly data
3. Compressing repeated data
4. Using shorter keys and values
"""

import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MonthlyDataOptimizer:
    """Optimizes monthly facility data for frontend embedding."""
    
    def __init__(self, db_path: str = "ice_locator_facilities.db"):
        self.db_path = db_path
    
    def get_facilities_and_monthly_data(self) -> Tuple[List[Dict], Dict[str, List[int]]]:
        """Get facilities metadata and monthly population data."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get facilities metadata
        cursor.execute("""
            SELECT id, name, latitude, longitude, address
            FROM facilities
            ORDER BY id
        """)
        
        facilities = []
        for row in cursor.fetchall():
            facilities.append({
                'i': row[0],  # id (shortened key)
                'n': row[1],  # name (shortened key)
                'lat': row[2],  # latitude (shortened key)
                'lng': row[3],  # longitude (shortened key)
                'a': row[4] or ''  # address (shortened key)
            })
        
        # Get monthly population data
        cursor.execute("""
            SELECT facility_id, month_year, population_count
            FROM monthly_population
            ORDER BY facility_id, month_year
        """)
        
        # Group by facility_id
        monthly_data = {}
        for row in cursor.fetchall():
            facility_id, month_year, population = row
            if facility_id not in monthly_data:
                monthly_data[facility_id] = []
            monthly_data[facility_id].append(population)
        
        conn.close()
        return facilities, monthly_data
    
    def get_available_months(self) -> List[str]:
        """Get list of available months in chronological order."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT month_year
            FROM monthly_population
            ORDER BY month_year
        """)
        
        months = [row[0] for row in cursor.fetchall()]
        conn.close()
        return months
    
    def create_optimized_structure(self) -> Dict:
        """Create optimized data structure."""
        logger.info("Creating optimized monthly data structure...")
        
        facilities, monthly_data = self.get_facilities_and_monthly_data()
        available_months = self.get_available_months()
        
        # Create month index mapping for even more compression
        month_index = {month: i for i, month in enumerate(available_months)}
        
        # Convert monthly data to arrays with month indices
        optimized_monthly_data = {}
        for facility_id, populations in monthly_data.items():
            # Create array where index corresponds to month_index
            population_array = [0] * len(available_months)
            for i, population in enumerate(populations):
                if i < len(available_months):
                    population_array[i] = population
            optimized_monthly_data[facility_id] = population_array
        
        # Create the optimized structure
        optimized_data = {
            'meta': {
                'v': 1,  # version
                't': datetime.now().isoformat(),  # timestamp
                'f': len(facilities),  # facility count
                'm': available_months,  # available months
                'l': available_months[-1] if available_months else None,  # latest month
                'd': 'ICE Detention Facilities - Optimized Monthly Data'
            },
            'facilities': facilities,
            'data': optimized_monthly_data
        }
        
        logger.info(f"Created optimized structure with {len(facilities)} facilities and {len(available_months)} months")
        return optimized_data
    
    def create_ultra_optimized_structure(self) -> Dict:
        """Create ultra-optimized structure with further compression."""
        logger.info("Creating ultra-optimized monthly data structure...")
        
        facilities, monthly_data = self.get_facilities_and_monthly_data()
        available_months = self.get_available_months()
        
        # Create month index mapping
        month_index = {month: i for i, month in enumerate(available_months)}
        
        # Ultra-compressed format: single array with facility_id, month_index, population
        compressed_data = []
        for facility_id, populations in monthly_data.items():
            for month_idx, population in enumerate(populations):
                if month_idx < len(available_months) and population > 0:
                    compressed_data.append([facility_id, month_idx, population])
        
        # Create the ultra-optimized structure
        ultra_optimized_data = {
            'meta': {
                'v': 2,  # version 2 for ultra-optimized
                't': datetime.now().isoformat(),
                'f': len(facilities),
                'm': available_months,
                'l': available_months[-1] if available_months else None,
                'd': 'ICE Detention Facilities - Ultra-Optimized Monthly Data'
            },
            'facilities': facilities,
            'data': compressed_data  # [facility_id, month_index, population] tuples
        }
        
        logger.info(f"Created ultra-optimized structure with {len(compressed_data)} data points")
        return ultra_optimized_data
    
    def export_optimized_data(self, output_file: str = "web-app/src/data/facilities_monthly_optimized.json"):
        """Export optimized data to file."""
        optimized_data = self.create_optimized_structure()
        
        with open(output_file, 'w') as f:
            json.dump(optimized_data, f, separators=(',', ':'))  # No spaces for smaller file
        
        # Get file size
        import os
        file_size = os.path.getsize(output_file)
        logger.info(f"Exported optimized data to {output_file} ({file_size:,} bytes)")
        
        return optimized_data
    
    def export_ultra_optimized_data(self, output_file: str = "web-app/src/data/facilities_monthly_ultra.json"):
        """Export ultra-optimized data to file."""
        ultra_optimized_data = self.create_ultra_optimized_structure()
        
        with open(output_file, 'w') as f:
            json.dump(ultra_optimized_data, f, separators=(',', ':'))  # No spaces for smaller file
        
        # Get file size
        import os
        file_size = os.path.getsize(output_file)
        logger.info(f"Exported ultra-optimized data to {output_file} ({file_size:,} bytes)")
        
        return ultra_optimized_data
    
    def compare_sizes(self):
        """Compare file sizes of different formats."""
        import os
        
        files_to_compare = [
            "web-app/src/data/facilities_monthly.json",
            "web-app/src/data/facilities_monthly_optimized.json",
            "web-app/src/data/facilities_monthly_ultra.json"
        ]
        
        logger.info("=== File Size Comparison ===")
        for file_path in files_to_compare:
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                logger.info(f"{file_path}: {size:,} bytes ({size/1024:.1f} KB)")
            else:
                logger.info(f"{file_path}: File not found")

def main():
    """Main entry point."""
    optimizer = MonthlyDataOptimizer()
    
    try:
        # Export both optimized versions
        optimizer.export_optimized_data()
        optimizer.export_ultra_optimized_data()
        
        # Compare sizes
        optimizer.compare_sizes()
        
        logger.info("Data optimization completed successfully")
    except Exception as e:
        logger.error(f"Data optimization failed: {e}")
        raise

if __name__ == "__main__":
    main()
