#!/usr/bin/env python3
"""
Check the SQLite database contents.
"""

import sqlite3
import os

def check_database():
    """Check the database contents."""
    db_path = "ice_locator_facilities.db"
    
    if not os.path.exists(db_path):
        print("❌ Database file not found")
        return
    
    try:
        connection = sqlite3.connect(db_path)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        
        # Get count
        cursor.execute("SELECT COUNT(*) as count FROM facilities")
        count = cursor.fetchone()[0]
        
        # Get total population
        cursor.execute("SELECT SUM(population_count) as total_pop FROM facilities WHERE population_count IS NOT NULL")
        total_pop = cursor.fetchone()[0] or 0
        
        # Get average population
        cursor.execute("SELECT AVG(population_count) as avg_pop FROM facilities WHERE population_count IS NOT NULL")
        avg_pop = cursor.fetchone()[0] or 0
        
        # Get sample facilities
        cursor.execute("SELECT name, city, state, population_count FROM facilities ORDER BY population_count DESC LIMIT 10")
        top_facilities = cursor.fetchall()
        
        print(f"📊 Database Status:")
        print(f"   Total facilities: {count}")
        print(f"   Total population: {total_pop:,}")
        print(f"   Average population: {avg_pop:.1f}")
        
        print(f"\n🏢 Top 10 Facilities by Population:")
        for facility in top_facilities:
            print(f"   {facility['name']} ({facility['city']}, {facility['state']}) - {facility['population_count']:,}")
        
        connection.close()
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")

if __name__ == "__main__":
    check_database()

