"""
Migration script to fix weekly PM data type mismatch
Converts boolean True/False values to 'X'/NULL for PM columns
"""

from database_utils import db_pool

# Database configuration
DB_CONFIG = {
    'host': 'ep-tiny-paper-ad8glt26-pooler.c-2.us-east-1.aws.neon.tech',
    'port': 5432,
    'database': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_2Nm6hyPVWiIH',
    'sslmode': 'require'
}

def fix_pm_data_types():
    """Convert boolean PM values to 'X'/NULL format"""
    print("Starting PM data type migration...")

    try:
        with db_pool.get_cursor(commit=True) as cursor:
            # First, let's check what types of data we have
            cursor.execute("""
                SELECT DISTINCT weekly_pm, monthly_pm, six_month_pm, annual_pm
                FROM equipment
                LIMIT 20
            """)
            print("\nSample of current PM values:")
            for row in cursor.fetchall():
                print(f"  Weekly: {row[0]}, Monthly: {row[1]}, Six Month: {row[2]}, Annual: {row[3]}")

            # Count equipment with boolean True values
            cursor.execute("""
                SELECT
                    COUNT(*) FILTER (WHERE weekly_pm::text IN ('true', 't', 'True', '1')) as weekly_count,
                    COUNT(*) FILTER (WHERE monthly_pm::text IN ('true', 't', 'True', '1')) as monthly_count,
                    COUNT(*) FILTER (WHERE six_month_pm::text IN ('true', 't', 'True', '1')) as six_month_count,
                    COUNT(*) FILTER (WHERE annual_pm::text IN ('true', 't', 'True', '1')) as annual_count
                FROM equipment
            """)
            counts = cursor.fetchone()
            print(f"\nEquipment with boolean True values:")
            print(f"  Weekly: {counts[0]}")
            print(f"  Monthly: {counts[1]}")
            print(f"  Six Month: {counts[2]}")
            print(f"  Annual: {counts[3]}")

            # Update weekly_pm: True -> 'X', False/NULL -> NULL
            print("\nUpdating weekly_pm column...")
            cursor.execute("""
                UPDATE equipment
                SET weekly_pm = CASE
                    WHEN weekly_pm::text IN ('true', 't', 'True', '1', 'X', 'x') THEN 'X'
                    ELSE NULL
                END
                WHERE weekly_pm IS NOT NULL
            """)
            print(f"  Updated {cursor.rowcount} rows")

            # Update monthly_pm: True -> 'X', False/NULL -> NULL
            print("Updating monthly_pm column...")
            cursor.execute("""
                UPDATE equipment
                SET monthly_pm = CASE
                    WHEN monthly_pm::text IN ('true', 't', 'True', '1', 'X', 'x') THEN 'X'
                    ELSE NULL
                END
                WHERE monthly_pm IS NOT NULL
            """)
            print(f"  Updated {cursor.rowcount} rows")

            # Update six_month_pm: True -> 'X', False/NULL -> NULL
            print("Updating six_month_pm column...")
            cursor.execute("""
                UPDATE equipment
                SET six_month_pm = CASE
                    WHEN six_month_pm::text IN ('true', 't', 'True', '1', 'X', 'x') THEN 'X'
                    ELSE NULL
                END
                WHERE six_month_pm IS NOT NULL
            """)
            print(f"  Updated {cursor.rowcount} rows")

            # Update annual_pm: True -> 'X', False/NULL -> NULL
            print("Updating annual_pm column...")
            cursor.execute("""
                UPDATE equipment
                SET annual_pm = CASE
                    WHEN annual_pm::text IN ('true', 't', 'True', '1', 'X', 'x') THEN 'X'
                    ELSE NULL
                END
                WHERE annual_pm IS NOT NULL
            """)
            print(f"  Updated {cursor.rowcount} rows")

            # Verify the changes
            print("\nVerifying changes...")
            cursor.execute("""
                SELECT
                    COUNT(*) FILTER (WHERE weekly_pm = 'X') as weekly_count,
                    COUNT(*) FILTER (WHERE monthly_pm = 'X') as monthly_count,
                    COUNT(*) FILTER (WHERE six_month_pm = 'X') as six_month_count,
                    COUNT(*) FILTER (WHERE annual_pm = 'X') as annual_count
                FROM equipment
            """)
            counts = cursor.fetchone()
            print(f"Equipment now with 'X' values:")
            print(f"  Weekly: {counts[0]}")
            print(f"  Monthly: {counts[1]}")
            print(f"  Six Month: {counts[2]}")
            print(f"  Annual: {counts[3]}")

            print("\n✓ Migration completed successfully!")

    except Exception as e:
        print(f"\n✗ Error during migration: {e}")
        raise

if __name__ == "__main__":
    # Initialize database connection pool
    print("Initializing database connection pool...")
    db_pool.initialize(DB_CONFIG, min_conn=1, max_conn=2)

    try:
        fix_pm_data_types()
    finally:
        # Clean up
        db_pool.close_all()
