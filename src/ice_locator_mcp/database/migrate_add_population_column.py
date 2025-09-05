"""
Migration script to add population_count column to facilities table.
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import os


def add_population_column(database_url: str):
    """
    Add population_count column to facilities table.
    
    Args:
        database_url: PostgreSQL connection string
    """
    connection = None
    try:
        # Connect to database
        connection = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
        cursor = connection.cursor()
        
        # Check if column already exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'facilities' AND column_name = 'population_count'
        """)
        
        if cursor.fetchone():
            print("Column 'population_count' already exists in facilities table")
        else:
            # Add the population_count column
            cursor.execute("""
                ALTER TABLE facilities 
                ADD COLUMN population_count INTEGER
            """)
            print("Added 'population_count' column to facilities table")
        
        # Commit changes
        connection.commit()
        cursor.close()
        
    except Exception as e:
        print(f"Error adding population_count column: {e}")
        if connection:
            connection.rollback()
    finally:
        if connection:
            connection.close()


def main():
    """Main function to run the migration."""
    # Get database URL from environment or use default
    database_url = os.environ.get(
        "DATABASE_URL", 
        "postgresql://localhost/ice_locator"
    )
    
    print("Running migration to add population_count column...")
    add_population_column(database_url)
    print("Migration completed.")


if __name__ == "__main__":
    main()