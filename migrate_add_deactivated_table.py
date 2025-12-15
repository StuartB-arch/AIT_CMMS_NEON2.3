"""
Migration script to add deactivated_assets table to existing database
Run this once to upgrade your database schema
"""

import psycopg2
from db_pool import db_pool

def migrate():
    """Add deactivated_assets table to database"""
    print("Starting migration: Adding deactivated_assets table...")

    try:
        with db_pool.get_cursor(commit=True) as cursor:
            # Check if table already exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'deactivated_assets'
                )
            """)

            table_exists = cursor.fetchone()[0]

            if table_exists:
                print("✓ Table 'deactivated_assets' already exists. No migration needed.")
                return

            # Create the deactivated_assets table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS deactivated_assets (
                    id SERIAL PRIMARY KEY,
                    bfm_equipment_no TEXT UNIQUE,
                    description TEXT,
                    location TEXT,
                    deactivated_by TEXT,
                    deactivated_date TEXT,
                    technician_name TEXT,
                    reason TEXT,
                    status TEXT DEFAULT 'Deactivated',
                    notes TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (bfm_equipment_no) REFERENCES equipment (bfm_equipment_no)
                )
            ''')

            print("✓ Successfully created 'deactivated_assets' table")
            print("✓ Migration complete!")

    except Exception as e:
        print(f"✗ Migration failed: {str(e)}")
        raise

if __name__ == "__main__":
    migrate()
