#!/usr/bin/env python3
"""
Clean up duplicate records in monthly_population table using entity discernment algorithm.
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any

def entity_discernment_algorithm(records: List[Dict]) -> Dict:
    """
    Entity discernment algorithm to determine the correct population count.
    
    Strategy:
    1. If multiple records exist for the same facility/month, take the most recent record
    2. Keep the most recent download_date, created_at, and population count
    3. This handles cases where facilities have multiple data collection points or updates
    """
    if not records:
        return None
    
    if len(records) == 1:
        return records[0]
    
    # Find the most recent record (by download_date, then created_at)
    most_recent = max(records, key=lambda r: (r['download_date'], r['created_at']))
    
    return {
        'id': most_recent['id'],  # Keep the most recent record's ID
        'facility_id': most_recent['facility_id'],
        'month_year': most_recent['month_year'],
        'population_count': most_recent['population_count'],  # Use most recent population count
        'download_date': most_recent['download_date'],
        'created_at': most_recent['created_at'],
        'original_record_count': len(records),
        'original_population_counts': [r['population_count'] for r in records],
        'records_to_remove': [r['id'] for r in records if r['id'] != most_recent['id']]
    }

def cleanup_duplicates(db_path: str = "ice_locator_facilities.db", dry_run: bool = True) -> Dict[str, Any]:
    """Clean up duplicate records using entity discernment algorithm."""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all duplicate groups
    cursor.execute("""
        SELECT facility_id, month_year, COUNT(*) as record_count
        FROM monthly_population 
        GROUP BY facility_id, month_year 
        HAVING COUNT(*) > 1
        ORDER BY facility_id, month_year
    """)
    duplicate_groups = cursor.fetchall()
    
    cleanup_log = {
        'cleanup_date': datetime.now().isoformat(),
        'dry_run': dry_run,
        'total_duplicate_groups': len(duplicate_groups),
        'processed_groups': [],
        'total_records_removed': 0,
        'total_records_updated': 0
    }
    
    print(f"Found {len(duplicate_groups)} duplicate groups to process...")
    
    for facility_id, month_year, record_count in duplicate_groups:
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
        
        # Apply entity discernment algorithm
        resolved_record = entity_discernment_algorithm(records)
        
        if resolved_record:
            # Get facility name for logging
            cursor.execute("SELECT name FROM facilities WHERE id = ?", (facility_id,))
            facility_result = cursor.fetchone()
            facility_name = facility_result[0] if facility_result else "Unknown"
            
            group_log = {
                'facility_id': facility_id,
                'facility_name': facility_name,
                'month_year': month_year,
                'original_record_count': len(records),
                'original_population_counts': [r['population_count'] for r in records],
                'resolved_population_count': resolved_record['population_count'],
                'kept_record_id': resolved_record['id'],
                'records_to_remove': [r['id'] for r in records if r['id'] != resolved_record['id']]
            }
            
            cleanup_log['processed_groups'].append(group_log)
            
            if not dry_run:
                # Update the kept record with the resolved population count
                cursor.execute("""
                    UPDATE monthly_population 
                    SET population_count = ?, download_date = ?, created_at = ?
                    WHERE id = ?
                """, (
                    resolved_record['population_count'],
                    resolved_record['download_date'],
                    resolved_record['created_at'],
                    resolved_record['id']
                ))
                
                # Remove duplicate records
                if resolved_record['records_to_remove']:
                    placeholders = ','.join(['?' for _ in resolved_record['records_to_remove']])
                    cursor.execute(f"""
                        DELETE FROM monthly_population 
                        WHERE id IN ({placeholders})
                    """, resolved_record['records_to_remove'])
                
                cleanup_log['total_records_updated'] += 1
                cleanup_log['total_records_removed'] += len(resolved_record['records_to_remove'])
            
            # Log progress
            if len(cleanup_log['processed_groups']) % 100 == 0:
                print(f"Processed {len(cleanup_log['processed_groups'])} groups...")
    
    if not dry_run:
        conn.commit()
        print(f"✅ Cleanup complete! Updated {cleanup_log['total_records_updated']} records, removed {cleanup_log['total_records_removed']} duplicates.")
    else:
        print(f"🔍 Dry run complete! Would update {len(cleanup_log['processed_groups'])} records.")
    
    conn.close()
    return cleanup_log

def save_cleanup_log(cleanup_log: Dict[str, Any], output_file: str = "cleanup_log.json"):
    """Save cleanup log to JSON file."""
    with open(output_file, 'w') as f:
        json.dump(cleanup_log, f, indent=2)
    print(f"Cleanup log saved to {output_file}")

if __name__ == "__main__":
    import sys
    
    dry_run = '--execute' not in sys.argv
    
    if dry_run:
        print("🔍 Running in DRY RUN mode. Use --execute to perform actual cleanup.")
    else:
        print("⚠️  EXECUTING ACTUAL CLEANUP. This will modify the database!")
        response = input("Are you sure? (yes/no): ")
        if response.lower() != 'yes':
            print("Cleanup cancelled.")
            sys.exit(0)
    
    print("Starting duplicate cleanup with entity discernment algorithm...")
    cleanup_log = cleanup_duplicates(dry_run=dry_run)
    
    # Save cleanup log
    save_cleanup_log(cleanup_log)
    
    # Show summary
    print(f"\n📊 CLEANUP SUMMARY:")
    print(f"Total duplicate groups: {cleanup_log['total_duplicate_groups']}")
    print(f"Processed groups: {len(cleanup_log['processed_groups'])}")
    
    if not dry_run:
        print(f"Records updated: {cleanup_log['total_records_updated']}")
        print(f"Records removed: {cleanup_log['total_records_removed']}")
    
    # Show some examples
    print(f"\n🔍 SAMPLE RESOLUTIONS:")
    for group in cleanup_log['processed_groups'][:3]:
        print(f"  {group['facility_name']} ({group['month_year']}):")
        print(f"    Original: {group['original_record_count']} records with counts {group['original_population_counts']}")
        print(f"    Resolved: {group['resolved_population_count']} (sum of all counts)")
        print(f"    Kept record ID: {group['kept_record_id']}")
        print(f"    Removed record IDs: {group['records_to_remove']}")
        print()
