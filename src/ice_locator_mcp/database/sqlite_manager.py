"""
SQLite database manager for the heatmap feature.
Handles SQLite database operations for detainees, facilities, and location history.
"""
import sqlite3
from typing import List, Optional, Dict
from datetime import datetime
from .models import Detainee, Facility, DetaineeLocationHistory


class SQLiteDatabaseManager:
    """Manages SQLite database connections and operations for the heatmap feature."""
    
    def __init__(self, database_path: str = "ice_locator_facilities.db"):
        """
        Initialize the SQLite database manager.
        
        Args:
            database_path: Path to the SQLite database file
        """
        self.database_path = database_path
        self.connection = None
    
    def connect(self):
        """Establish a connection to the SQLite database."""
        try:
            self.connection = sqlite3.connect(self.database_path)
            self.connection.row_factory = sqlite3.Row  # Enable column access by name
        except Exception as e:
            print(f"Error connecting to SQLite database: {e}")
            raise
    
    def disconnect(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def create_tables(self):
        """Create the database tables if they don't exist."""
        if not self.connection:
            raise Exception("Database not connected")
        
        cursor = self.connection.cursor()
        
        # Create Detainee table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS detainees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create Facility table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS facilities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                address TEXT,
                population_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create DetaineeLocationHistory table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS detainee_location_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                detainee_id INTEGER NOT NULL,
                facility_id INTEGER NOT NULL,
                start_date TIMESTAMP NOT NULL,
                end_date TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (detainee_id) REFERENCES detainees (id),
                FOREIGN KEY (facility_id) REFERENCES facilities (id)
            )
        """)
        
        # Create indexes for better performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_detainee_location_detainee_id 
            ON detainee_location_history (detainee_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_detainee_location_facility_id 
            ON detainee_location_history (facility_id)
        """)
        
        self.connection.commit()
    
    def get_all_facilities(self) -> List[Facility]:
        """Get all facilities from the database."""
        if not self.connection:
            raise Exception("Database not connected")
        
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT id, name, latitude, longitude, address, population_count, created_at, updated_at
            FROM facilities
            ORDER BY name
        """)
        
        facilities = []
        for row in cursor.fetchall():
            facility = Facility(
                id=row['id'],
                name=row['name'],
                latitude=row['latitude'],
                longitude=row['longitude'],
                address=row['address'],
                population_count=row['population_count'],
                created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
            )
            facilities.append(facility)
        
        return facilities
    
    def get_facility_by_id(self, facility_id: int) -> Optional[Facility]:
        """Get a specific facility by ID."""
        if not self.connection:
            raise Exception("Database not connected")
        
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT id, name, latitude, longitude, address, population_count, created_at, updated_at
            FROM facilities
            WHERE id = ?
        """, (facility_id,))
        
        row = cursor.fetchone()
        if row:
            return Facility(
                id=row['id'],
                name=row['name'],
                latitude=row['latitude'],
                longitude=row['longitude'],
                address=row['address'],
                population_count=row['population_count'],
                created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
            )
        return None
    
    def get_current_detainee_count_by_facility(self) -> List[Dict]:
        """Get current detainee count for each facility."""
        if not self.connection:
            raise Exception("Database not connected")
        
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT 
                facility_id,
                COUNT(*) as detainee_count
            FROM detainee_location_history
            WHERE end_date IS NULL
            GROUP BY facility_id
        """)
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_heatmap_data(self) -> List[Dict]:
        """Get aggregated data for heatmap visualization."""
        if not self.connection:
            raise Exception("Database not connected")
        
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT 
                f.id,
                f.name,
                f.latitude,
                f.longitude,
                f.address,
                f.population_count,
                COALESCE(COUNT(dlh.detainee_id), 0) as current_detainee_count
            FROM facilities f
            LEFT JOIN detainee_location_history dlh ON f.id = dlh.facility_id AND dlh.end_date IS NULL
            GROUP BY f.id, f.name, f.latitude, f.longitude, f.address, f.population_count
            ORDER BY f.population_count DESC
        """)
        
        heatmap_data = []
        for row in cursor.fetchall():
            heatmap_data.append({
                "id": row['id'],
                "name": row['name'],
                "latitude": row['latitude'],
                "longitude": row['longitude'],
                "address": row['address'],
                "population_count": row['population_count'],
                "current_detainee_count": row['current_detainee_count']
            })
        
        return heatmap_data
    
    def get_facilities_with_population(self) -> List[Dict]:
        """Get all facilities with their population counts for heatmap visualization."""
        if not self.connection:
            raise Exception("Database not connected")
        
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT 
                id,
                name,
                latitude,
                longitude,
                address,
                population_count,
                created_at,
                updated_at
            FROM facilities
            WHERE population_count IS NOT NULL AND population_count > 0
            ORDER BY population_count DESC
        """)
        
        facilities = []
        for row in cursor.fetchall():
            facilities.append({
                "id": row['id'],
                "name": row['name'],
                "latitude": row['latitude'],
                "longitude": row['longitude'],
                "address": row['address'],
                "population_count": row['population_count'],
                "created_at": row['created_at'],
                "updated_at": row['updated_at']
            })
        
        return facilities
    
    def get_facility_statistics(self) -> Dict:
        """Get overall facility statistics."""
        if not self.connection:
            raise Exception("Database not connected")
        
        cursor = self.connection.cursor()
        
        # Total facilities
        cursor.execute("SELECT COUNT(*) as total_facilities FROM facilities")
        total_facilities = cursor.fetchone()['total_facilities']
        
        # Total population
        cursor.execute("SELECT SUM(population_count) as total_population FROM facilities WHERE population_count IS NOT NULL")
        total_population = cursor.fetchone()['total_population'] or 0
        
        # Average population
        cursor.execute("SELECT AVG(population_count) as avg_population FROM facilities WHERE population_count IS NOT NULL")
        avg_population = cursor.fetchone()['avg_population'] or 0
        
        # Facilities by state (extract from address)
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN address LIKE '%, CA%' THEN 'CA'
                    WHEN address LIKE '%, TX%' THEN 'TX'
                    WHEN address LIKE '%, FL%' THEN 'FL'
                    WHEN address LIKE '%, AZ%' THEN 'AZ'
                    WHEN address LIKE '%, NM%' THEN 'NM'
                    WHEN address LIKE '%, CO%' THEN 'CO'
                    WHEN address LIKE '%, NJ%' THEN 'NJ'
                    WHEN address LIKE '%, MI%' THEN 'MI'
                    WHEN address LIKE '%, VA%' THEN 'VA'
                    WHEN address LIKE '%, LA%' THEN 'LA'
                    WHEN address LIKE '%, GA%' THEN 'GA'
                    WHEN address LIKE '%, AL%' THEN 'AL'
                    WHEN address LIKE '%, MS%' THEN 'MS'
                    WHEN address LIKE '%, TN%' THEN 'TN'
                    WHEN address LIKE '%, KY%' THEN 'KY'
                    WHEN address LIKE '%, OH%' THEN 'OH'
                    WHEN address LIKE '%, PA%' THEN 'PA'
                    WHEN address LIKE '%, NY%' THEN 'NY'
                    WHEN address LIKE '%, WA%' THEN 'WA'
                    WHEN address LIKE '%, OR%' THEN 'OR'
                    WHEN address LIKE '%, NV%' THEN 'NV'
                    WHEN address LIKE '%, UT%' THEN 'UT'
                    WHEN address LIKE '%, MT%' THEN 'MT'
                    WHEN address LIKE '%, ND%' THEN 'ND'
                    WHEN address LIKE '%, SD%' THEN 'SD'
                    WHEN address LIKE '%, NE%' THEN 'NE'
                    WHEN address LIKE '%, KS%' THEN 'KS'
                    WHEN address LIKE '%, OK%' THEN 'OK'
                    WHEN address LIKE '%, AR%' THEN 'AR'
                    WHEN address LIKE '%, MO%' THEN 'MO'
                    WHEN address LIKE '%, IA%' THEN 'IA'
                    WHEN address LIKE '%, MN%' THEN 'MN'
                    WHEN address LIKE '%, WI%' THEN 'WI'
                    WHEN address LIKE '%, IL%' THEN 'IL'
                    WHEN address LIKE '%, IN%' THEN 'IN'
                    WHEN address LIKE '%, WV%' THEN 'WV'
                    WHEN address LIKE '%, NC%' THEN 'NC'
                    WHEN address LIKE '%, SC%' THEN 'SC'
                    WHEN address LIKE '%, ME%' THEN 'ME'
                    WHEN address LIKE '%, VT%' THEN 'VT'
                    WHEN address LIKE '%, NH%' THEN 'NH'
                    WHEN address LIKE '%, MA%' THEN 'MA'
                    WHEN address LIKE '%, RI%' THEN 'RI'
                    WHEN address LIKE '%, CT%' THEN 'CT'
                    WHEN address LIKE '%, DE%' THEN 'DE'
                    WHEN address LIKE '%, MD%' THEN 'MD'
                    WHEN address LIKE '%, AK%' THEN 'AK'
                    WHEN address LIKE '%, HI%' THEN 'HI'
                    ELSE 'Other'
                END as state,
                COUNT(*) as facility_count,
                SUM(population_count) as state_population
            FROM facilities
            WHERE population_count IS NOT NULL
            GROUP BY state
            ORDER BY state_population DESC
        """)
        
        facilities_by_state = [dict(row) for row in cursor.fetchall()]
        
        return {
            "total_facilities": total_facilities,
            "total_population": total_population,
            "average_population": round(avg_population, 1),
            "facilities_by_state": facilities_by_state
        }

