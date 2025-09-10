#!/usr/bin/env python3
"""
Script to check database statistics for heatmap data issue.
"""
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ice_locator_mcp.database.manager import DatabaseManager

def check_database_stats():
    """Check database statistics to understand the heatmap data issue."""
    db = DatabaseManager('postgresql://localhost/ice_locator')
    db.connect()
    
    try:
        cursor = db.connection.cursor()
        
        # Check total records
        cursor.execute('SELECT COUNT(*) as total FROM detainee_location_history')
        total = cursor.fetchone()['total']
        
        cursor.execute('SELECT COUNT(*) as current FROM detainee_location_history WHERE end_date IS NULL')
        current = cursor.fetchone()['current']
        
        print(f'Total location records: {total}')
        print(f'Current location records: {current}')
        
        # Check top facilities by detainee count
        cursor.execute('''
            SELECT f.id, f.name, COUNT(dlh.id) as count 
            FROM facilities f
            LEFT JOIN detainee_location_history dlh ON f.id = dlh.facility_id 
            WHERE dlh.end_date IS NULL
            GROUP BY f.id, f.name
            ORDER BY count DESC
            LIMIT 10
        ''')
        top_facilities = cursor.fetchall()
        
        print('\nTop facilities by detainee count:')
        for row in top_facilities:
            print(f'  {row["name"]}: {row["count"]} detainees')
        
        # Check a specific facility that should have detainees
        cursor.execute('''
            SELECT f.name, COUNT(dlh.id) as count
            FROM facilities f
            LEFT JOIN detainee_location_history dlh ON f.id = dlh.facility_id
            WHERE f.name = 'Florida State Prison' AND dlh.end_date IS NULL
            GROUP BY f.name
        ''')
        florida_prison = cursor.fetchone()
        print(f"\nFlorida State Prison detainees: {florida_prison['count'] if florida_prison else 0}")
        
        cursor.close()
        
    finally:
        db.disconnect()

if __name__ == "__main__":
    check_database_stats()