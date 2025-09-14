#!/usr/bin/env python3
"""
Analyze duplicate records in monthly_population table for entity discernment testing.
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any

def analyze_duplicates(db_path: str = "ice_locator_facilities.db") -> Dict[str, Any]:
    """Analyze duplicate records in the monthly_population table."""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get total duplicate groups
    cursor.execute("""
        SELECT COUNT(*) as total_duplicate_groups 
        FROM (
            SELECT facility_id, month_year 
            FROM monthly_population 
            GROUP BY facility_id, month_year 
            HAVING COUNT(*) > 1
        )
    """)
    total_duplicate_groups = cursor.fetchone()[0]
    
    # Get facilities with most duplicates
    cursor.execute("""
        SELECT facility_id, COUNT(*) as duplicate_groups 
        FROM (
            SELECT facility_id, month_year 
            FROM monthly_population 
            GROUP BY facility_id, month_year 
            HAVING COUNT(*) > 1
        ) 
        GROUP BY facility_id 
        ORDER BY duplicate_groups DESC 
        LIMIT 10
    """)
    top_duplicate_facilities = cursor.fetchall()
    
    # Get facility names for top duplicates
    facility_ids = [row[0] for row in top_duplicate_facilities]
    placeholders = ','.join(['?' for _ in facility_ids])
    cursor.execute(f"""
        SELECT id, name, address 
        FROM facilities 
        WHERE id IN ({placeholders})
        ORDER BY id
    """, facility_ids)
    facility_info = {row[0]: {'name': row[1], 'address': row[2]} for row in cursor.fetchall()}
    
    # Collect sample duplicate records for testing
    sample_duplicates = []
    for facility_id, duplicate_count in top_duplicate_facilities[:3]:  # Top 3 facilities
        cursor.execute("""
            SELECT facility_id, month_year, COUNT(*) as record_count
            FROM monthly_population 
            WHERE facility_id = ?
            GROUP BY facility_id, month_year 
            HAVING COUNT(*) > 1
            ORDER BY record_count DESC
            LIMIT 3
        """, (facility_id,))
        
        for facility_id, month_year, record_count in cursor.fetchall():
            # Get all records for this facility/month combination
            cursor.execute("""
                SELECT id, facility_id, month_year, population_count, download_date, created_at
                FROM monthly_population 
                WHERE facility_id = ? AND month_year = ?
                ORDER BY download_date, created_at
            """, (facility_id, month_year))
            
            records = []
            for row in cursor.fetchall():
                records.append({
                    'id': row[0],
                    'facility_id': row[1],
                    'month_year': row[2],
                    'population_count': row[3],
                    'download_date': row[4],
                    'created_at': row[5]
                })
            
            sample_duplicates.append({
                'facility_id': facility_id,
                'facility_name': facility_info[facility_id]['name'],
                'facility_address': facility_info[facility_id]['address'],
                'month_year': month_year,
                'record_count': record_count,
                'records': records
            })
    
    conn.close()
    
    return {
        'analysis_date': datetime.now().isoformat(),
        'total_duplicate_groups': total_duplicate_groups,
        'top_duplicate_facilities': [
            {
                'facility_id': row[0],
                'facility_name': facility_info[row[0]]['name'],
                'facility_address': facility_info[row[0]]['address'],
                'duplicate_groups': row[1]
            }
            for row in top_duplicate_facilities
        ],
        'sample_duplicates': sample_duplicates
    }

def save_duplicate_analysis(analysis: Dict[str, Any], output_file: str = "duplicate_analysis.json"):
    """Save duplicate analysis to JSON file."""
    with open(output_file, 'w') as f:
        json.dump(analysis, f, indent=2)
    print(f"Duplicate analysis saved to {output_file}")

if __name__ == "__main__":
    print("Analyzing duplicate records in monthly_population table...")
    analysis = analyze_duplicates()
    
    print(f"\n📊 DUPLICATE ANALYSIS RESULTS:")
    print(f"Total duplicate groups: {analysis['total_duplicate_groups']}")
    print(f"\nTop facilities with duplicates:")
    for facility in analysis['top_duplicate_facilities']:
        print(f"  - {facility['facility_name']} (ID: {facility['facility_id']}): {facility['duplicate_groups']} duplicate groups")
    
    print(f"\nSample duplicate records collected for testing entity discernment algorithm.")
    
    # Save analysis
    save_duplicate_analysis(analysis)
    
    # Print sample for review
    print(f"\n🔍 SAMPLE DUPLICATE RECORDS:")
    for sample in analysis['sample_duplicates'][:2]:  # Show first 2 samples
        print(f"\nFacility: {sample['facility_name']} (ID: {sample['facility_id']})")
        print(f"Month: {sample['month_year']} - {sample['record_count']} duplicate records")
        print("Records:")
        for record in sample['records']:
            print(f"  ID: {record['id']}, Population: {record['population_count']}, Download: {record['download_date']}, Created: {record['created_at']}")
