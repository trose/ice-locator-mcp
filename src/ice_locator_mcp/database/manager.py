"""
Database manager for the heatmap feature.
Handles PostgreSQL database operations for detainees, facilities, and location history.
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Optional
from datetime import datetime
from .models import Detainee, Facility, DetaineeLocationHistory


class DatabaseManager:
    """Manages database connections and operations for the heatmap feature."""
    
    def __init__(self, database_url: str):
        """
        Initialize the database manager.
        
        Args:
            database_url: PostgreSQL connection string
        """
        self.database_url = database_url
        self.connection = None
    
    def connect(self):
        """Establish a connection to the database."""
        try:
            self.connection = psycopg2.connect(self.database_url, cursor_factory=RealDictCursor)
        except Exception as e:
            print(f"Error connecting to database: {e}")
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
                id SERIAL PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create Facility table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS facilities (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create DetaineeLocationHistory table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS detainee_location_history (
                id SERIAL PRIMARY KEY,
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
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_facility_name 
            ON facilities (name)
        """)
        
        self.connection.commit()
        cursor.close()
    
    def insert_detainee(self, detainee: Detainee) -> int:
        """
        Insert a new detainee into the database.
        
        Args:
            detainee: Detainee object to insert
            
        Returns:
            The ID of the inserted detainee
        """
        if not self.connection:
            raise Exception("Database not connected")
        
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO detainees (first_name, last_name, created_at, updated_at)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (
            detainee.first_name,
            detainee.last_name,
            detainee.created_at or datetime.now(),
            detainee.updated_at or datetime.now()
        ))
        
        detainee_id = cursor.fetchone()['id']
        self.connection.commit()
        cursor.close()
        
        return detainee_id
    
    def insert_facility(self, facility: Facility) -> int:
        """
        Insert a new facility into the database.
        
        Args:
            facility: Facility object to insert
            
        Returns:
            The ID of the inserted facility
        """
        if not self.connection:
            raise Exception("Database not connected")
        
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO facilities (name, latitude, longitude, address, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            facility.name,
            facility.latitude,
            facility.longitude,
            facility.address,
            facility.created_at or datetime.now(),
            facility.updated_at or datetime.now()
        ))
        
        facility_id = cursor.fetchone()['id']
        self.connection.commit()
        cursor.close()
        
        return facility_id
    
    def insert_location_history(self, location_history: DetaineeLocationHistory) -> int:
        """
        Insert a new location history record into the database.
        
        Args:
            location_history: DetaineeLocationHistory object to insert
            
        Returns:
            The ID of the inserted record
        """
        if not self.connection:
            raise Exception("Database not connected")
        
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO detainee_location_history 
            (detainee_id, facility_id, start_date, end_date, created_at)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (
            location_history.detainee_id,
            location_history.facility_id,
            location_history.start_date,
            location_history.end_date,
            location_history.created_at or datetime.now()
        ))
        
        history_id = cursor.fetchone()['id']
        self.connection.commit()
        cursor.close()
        
        return history_id
    
    def get_all_facilities(self) -> List[Facility]:
        """
        Retrieve all facilities from the database.
        
        Returns:
            List of Facility objects
        """
        if not self.connection:
            raise Exception("Database not connected")
        
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT id, name, latitude, longitude, address, created_at, updated_at
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
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
            facilities.append(facility)
        
        cursor.close()
        return facilities
    
    def get_current_detainee_count_by_facility(self) -> List[dict]:
        """
        Get current detainee count for each facility.
        
        Returns:
            List of dictionaries with facility_id and detainee_count
        """
        if not self.connection:
            raise Exception("Database not connected")
        
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT f.id as facility_id, f.name as facility_name, COUNT(dlh.id) as detainee_count
            FROM facilities f
            LEFT JOIN detainee_location_history dlh ON f.id = dlh.facility_id 
            AND dlh.end_date IS NULL
            GROUP BY f.id, f.name
            ORDER BY f.name
        """)
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'facility_id': row['facility_id'],
                'facility_name': row['facility_name'],
                'detainee_count': row['detainee_count']
            })
        
        cursor.close()
        return results
    
    def get_heatmap_data(self) -> List[dict]:
        """
        Get aggregated data for heatmap visualization.
        
        Returns:
            List of dictionaries with facility coordinates and detainee counts
        """
        if not self.connection:
            raise Exception("Database not connected")
        
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT f.id, f.name, f.latitude, f.longitude, f.address, COUNT(dlh.id) as detainee_count
            FROM facilities f
            LEFT JOIN detainee_location_history dlh ON f.id = dlh.facility_id 
            AND dlh.end_date IS NULL
            GROUP BY f.id, f.name, f.latitude, f.longitude, f.address
            ORDER BY f.name
        """)
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row['id'],
                'name': row['name'],
                'latitude': row['latitude'],
                'longitude': row['longitude'],
                'address': row['address'],
                'detainee_count': row['detainee_count']
            })
        
        cursor.close()
        return results
    
    def get_facilities_without_coordinates(self) -> List[Facility]:
        """
        Retrieve facilities that have missing or invalid coordinates (0.0, 0.0).
        
        Returns:
            List of Facility objects without valid coordinates
        """
        if not self.connection:
            raise Exception("Database not connected")
        
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT id, name, latitude, longitude, address, created_at, updated_at
            FROM facilities
            WHERE latitude = 0.0 AND longitude = 0.0
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
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
            facilities.append(facility)
        
        cursor.close()
        return facilities
