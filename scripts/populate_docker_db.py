#!/usr/bin/env python3
"""
Populate the Dockerized PostgreSQL database with comprehensive facility data.
"""

import json
import psycopg2
import time
from datetime import datetime
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

class DockerDatabasePopulator:
    def __init__(self, database_url="postgresql://ice_user:ice_password@localhost:5432/ice_locator"):
        self.database_url = database_url
        self.geolocator = Nominatim(user_agent="ice_locator_docker_populator")
        self.connection = None
        
    def connect_database(self):
        """Connect to the PostgreSQL database."""
        try:
            self.connection = psycopg2.connect(self.database_url)
            print(f"✅ Connected to PostgreSQL database")
        except Exception as e:
            print(f"❌ Error connecting to database: {e}")
            raise
    
    def disconnect_database(self):
        """Disconnect from the database."""
        if self.connection:
            self.connection.close()
            self.connection = None
            print("✅ Disconnected from database")
    
    def clear_existing_data(self):
        """Clear existing facilities data."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM facilities")
            self.connection.commit()
            print("🗑️ Cleared existing facilities data")
        except Exception as e:
            print(f"❌ Error clearing data: {e}")
            raise
    
    def geocode_address(self, facility_name, city, state, zip_code):
        """Geocode an address to get latitude and longitude."""
        try:
            # Construct address
            address = f"{facility_name}, {city}, {state}, {zip_code}"
            
            # Try geocoding with a delay to respect rate limits
            time.sleep(1)  # 1 second delay between requests
            
            location = self.geolocator.geocode(address, timeout=10)
            
            if location:
                return location.latitude, location.longitude, address
            else:
                # Try with just city, state, zip
                fallback_address = f"{city}, {state}, {zip_code}"
                location = self.geolocator.geocode(fallback_address, timeout=10)
                
                if location:
                    return location.latitude, location.longitude, fallback_address
                else:
                    # Use default coordinates (center of US)
                    return 39.8283, -98.5795, f"{city}, {state}, {zip_code} (default coordinates)"
                    
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            print(f"⚠️ Geocoding error for {facility_name}: {e}")
            return 39.8283, -98.5795, f"{city}, {state}, {zip_code} (geocoding failed)"
        except Exception as e:
            print(f"⚠️ Unexpected error geocoding {facility_name}: {e}")
            return 39.8283, -98.5795, f"{city}, {state}, {zip_code} (error)"
    
    def insert_facility(self, facility):
        """Insert a facility into the database."""
        try:
            cursor = self.connection.cursor()
            
            # Geocode the address
            lat, lng, address = self.geocode_address(
                facility['name'],
                facility['city'],
                facility['state'],
                facility['zip']
            )
            
            # Insert facility
            cursor.execute("""
                INSERT INTO facilities (
                    name, latitude, longitude, address, population_count, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                facility['name'],
                lat,
                lng,
                address,
                facility['population'],
                datetime.now(),
                datetime.now()
            ))
            
            self.connection.commit()
            return True
            
        except Exception as e:
            print(f"❌ Error inserting facility {facility['name']}: {e}")
            return False
    
    def populate_database(self, facilities_file="comprehensive_ice_facilities.json"):
        """Populate the database with comprehensive facilities data."""
        print("🚀 Starting Docker database population...")
        
        # Load facilities data
        try:
            with open(facilities_file, 'r') as f:
                facilities = json.load(f)
            print(f"📋 Loaded {len(facilities)} facilities from {facilities_file}")
        except Exception as e:
            print(f"❌ Error loading facilities file: {e}")
            return
        
        # Connect to database
        self.connect_database()
        
        try:
            # Clear existing data
            self.clear_existing_data()
            
            # Insert new facilities
            successful_inserts = 0
            failed_inserts = 0
            
            for i, facility in enumerate(facilities, 1):
                print(f"📝 Processing facility {i}/{len(facilities)}: {facility['name']}")
                
                if self.insert_facility(facility):
                    successful_inserts += 1
                    print(f"   ✅ Inserted: {facility['name']}")
                else:
                    failed_inserts += 1
                    print(f"   ❌ Failed: {facility['name']}")
                
                # Progress update every 10 facilities
                if i % 10 == 0:
                    print(f"   📊 Progress: {i}/{len(facilities)} ({i/len(facilities)*100:.1f}%)")
            
            print(f"\n🎉 Database population complete!")
            print(f"✅ Successfully inserted: {successful_inserts} facilities")
            print(f"❌ Failed to insert: {failed_inserts} facilities")
            
            # Get final statistics
            self.get_database_statistics()
            
        except Exception as e:
            print(f"❌ Error during database population: {e}")
        finally:
            self.disconnect_database()
    
    def get_database_statistics(self):
        """Get and display database statistics."""
        try:
            cursor = self.connection.cursor()
            
            # Total facilities
            cursor.execute("SELECT COUNT(*) FROM facilities")
            total_facilities = cursor.fetchone()[0]
            
            # Total population
            cursor.execute("SELECT SUM(population_count) FROM facilities WHERE population_count IS NOT NULL")
            total_population = cursor.fetchone()[0] or 0
            
            # Average population
            cursor.execute("SELECT AVG(population_count) FROM facilities WHERE population_count IS NOT NULL")
            avg_population = cursor.fetchone()[0] or 0
            
            print(f"\n📊 Final Database Statistics:")
            print(f"   Total facilities: {total_facilities}")
            print(f"   Total population: {total_population:,}")
            print(f"   Average population: {avg_population:.1f}")
            
            # Top facilities by population
            cursor.execute("""
                SELECT name, population_count 
                FROM facilities 
                WHERE population_count IS NOT NULL 
                ORDER BY population_count DESC 
                LIMIT 5
            """)
            
            top_facilities = cursor.fetchall()
            print(f"\n🏆 Top 5 facilities by population:")
            for i, (name, population) in enumerate(top_facilities, 1):
                print(f"   {i}. {name} - {population:,}")
            
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")

def main():
    """Main function."""
    populator = DockerDatabasePopulator()
    populator.populate_database()

if __name__ == "__main__":
    main()

