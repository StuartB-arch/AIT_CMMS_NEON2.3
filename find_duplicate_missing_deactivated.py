#!/usr/bin/env python3
"""
Script to find assets that appear in BOTH the cannot_find_assets and deactivated_assets tables.
These are duplicates that should be removed from the cannot_find list since they're deactivated.
"""

import psycopg2
from psycopg2 import pool
import sys
from datetime import datetime

def get_database_connection():
    """Create and return a database connection."""
    try:
        # NEON Cloud Database Configuration (from AIT_CMMS_REV3.py)
        conn = psycopg2.connect(
            host='ep-tiny-paper-ad8glt26-pooler.c-2.us-east-1.aws.neon.tech',
            port=5432,
            database='neondb',
            user='neondb_owner',
            password='npg_2Nm6hyPVWiIH',
            sslmode='require',
            connect_timeout=30
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)

def find_duplicate_assets():
    """Find assets that are in both cannot_find and deactivated tables."""

    conn = get_database_connection()
    cursor = conn.cursor()

    try:
        # Query to find assets in BOTH tables
        query = """
        SELECT
            cf.bfm_equipment_no,
            e.sap_material_no,
            e.description,
            cf.location as cannot_find_location,
            cf.reported_by,
            cf.reported_date,
            cf.status as cannot_find_status,
            d.deactivated_by,
            d.deactivated_date,
            d.reason as deactivation_reason,
            d.status as deactivated_status
        FROM cannot_find_assets cf
        INNER JOIN deactivated_assets d ON cf.bfm_equipment_no = d.bfm_equipment_no
        LEFT JOIN equipment e ON cf.bfm_equipment_no = e.bfm_equipment_no
        WHERE cf.status = 'Missing'
        ORDER BY cf.bfm_equipment_no;
        """

        cursor.execute(query)
        results = cursor.fetchall()

        if not results:
            print("\n✓ No duplicate assets found!")
            print("All Cannot Find assets are properly separated from Deactivated assets.")
            return []

        # Print header
        print("\n" + "="*120)
        print("ASSETS FOUND IN BOTH 'CANNOT FIND' AND 'DEACTIVATED' LISTS")
        print("="*120)
        print(f"\nTotal duplicates found: {len(results)}\n")

        # Print detailed table
        print(f"{'BFM Number':<15} {'SAP Number':<12} {'Description':<35} {'Deactivated Date':<17} {'Deactivation Reason':<30}")
        print("-"*120)

        duplicate_bfm_numbers = []

        for row in results:
            bfm_no = row[0] or "N/A"
            sap_no = row[1] or "N/A"
            description = (row[2] or "N/A")[:33]  # Truncate long descriptions
            deactivated_date = row[8] or "N/A"
            reason = (row[9] or "N/A")[:28]  # Truncate long reasons

            print(f"{bfm_no:<15} {sap_no:<12} {description:<35} {deactivated_date:<17} {reason:<30}")
            duplicate_bfm_numbers.append(bfm_no)

        # Print detailed information
        print("\n" + "="*120)
        print("DETAILED INFORMATION")
        print("="*120)

        for idx, row in enumerate(results, 1):
            print(f"\n[{idx}] BFM Number: {row[0]}")
            print(f"    SAP Number: {row[1] or 'N/A'}")
            print(f"    Description: {row[2] or 'N/A'}")
            print(f"    ---")
            print(f"    Cannot Find Location: {row[3] or 'N/A'}")
            print(f"    Reported By: {row[4] or 'N/A'}")
            print(f"    Reported Date: {row[5] or 'N/A'}")
            print(f"    Cannot Find Status: {row[6] or 'N/A'}")
            print(f"    ---")
            print(f"    Deactivated By: {row[7] or 'N/A'}")
            print(f"    Deactivated Date: {row[8] or 'N/A'}")
            print(f"    Deactivation Reason: {row[9] or 'N/A'}")
            print(f"    Deactivated Status: {row[10] or 'N/A'}")

        # Print summary list of BFM numbers
        print("\n" + "="*120)
        print("BFM NUMBERS TO REMOVE FROM 'CANNOT FIND' LIST")
        print("="*120)
        print("\nCopy this list to remove these assets from the Cannot Find table:\n")
        for bfm in duplicate_bfm_numbers:
            print(f"  {bfm}")

        # Save to file
        output_file = f"duplicate_assets_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(output_file, 'w') as f:
            f.write("="*120 + "\n")
            f.write("ASSETS FOUND IN BOTH 'CANNOT FIND' AND 'DEACTIVATED' LISTS\n")
            f.write("="*120 + "\n")
            f.write(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total duplicates found: {len(results)}\n\n")

            f.write(f"{'BFM Number':<15} {'SAP Number':<12} {'Description':<35} {'Deactivated Date':<17} {'Deactivation Reason':<30}\n")
            f.write("-"*120 + "\n")

            for row in results:
                bfm_no = row[0] or "N/A"
                sap_no = row[1] or "N/A"
                description = (row[2] or "N/A")[:33]
                deactivated_date = row[8] or "N/A"
                reason = (row[9] or "N/A")[:28]
                f.write(f"{bfm_no:<15} {sap_no:<12} {description:<35} {deactivated_date:<17} {reason:<30}\n")

            f.write("\n" + "="*120 + "\n")
            f.write("DETAILED INFORMATION\n")
            f.write("="*120 + "\n")

            for idx, row in enumerate(results, 1):
                f.write(f"\n[{idx}] BFM Number: {row[0]}\n")
                f.write(f"    SAP Number: {row[1] or 'N/A'}\n")
                f.write(f"    Description: {row[2] or 'N/A'}\n")
                f.write(f"    ---\n")
                f.write(f"    Cannot Find Location: {row[3] or 'N/A'}\n")
                f.write(f"    Reported By: {row[4] or 'N/A'}\n")
                f.write(f"    Reported Date: {row[5] or 'N/A'}\n")
                f.write(f"    Cannot Find Status: {row[6] or 'N/A'}\n")
                f.write(f"    ---\n")
                f.write(f"    Deactivated By: {row[7] or 'N/A'}\n")
                f.write(f"    Deactivated Date: {row[8] or 'N/A'}\n")
                f.write(f"    Deactivation Reason: {row[9] or 'N/A'}\n")
                f.write(f"    Deactivated Status: {row[10] or 'N/A'}\n")

            f.write("\n" + "="*120 + "\n")
            f.write("BFM NUMBERS TO REMOVE FROM 'CANNOT FIND' LIST\n")
            f.write("="*120 + "\n\n")
            for bfm in duplicate_bfm_numbers:
                f.write(f"  {bfm}\n")

        print(f"\n✓ Full report saved to: {output_file}")

        return duplicate_bfm_numbers

    except Exception as e:
        print(f"Error querying database: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        cursor.close()
        conn.close()

def generate_cleanup_sql(bfm_numbers):
    """Generate SQL statements to remove duplicates from cannot_find_assets table."""

    if not bfm_numbers:
        return

    sql_file = f"cleanup_duplicate_assets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"

    with open(sql_file, 'w') as f:
        f.write("-- SQL Script to Remove Duplicate Assets from Cannot Find List\n")
        f.write(f"-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"-- Total assets to remove: {len(bfm_numbers)}\n\n")
        f.write("-- BACKUP FIRST: Create a backup of cannot_find_assets table\n")
        f.write("-- CREATE TABLE cannot_find_assets_backup AS SELECT * FROM cannot_find_assets;\n\n")
        f.write("BEGIN;\n\n")

        for bfm in bfm_numbers:
            f.write(f"DELETE FROM cannot_find_assets WHERE bfm_equipment_no = '{bfm}';\n")

        f.write("\n-- Review the changes before committing\n")
        f.write("-- If everything looks good, run: COMMIT;\n")
        f.write("-- If you want to undo, run: ROLLBACK;\n\n")
        f.write("-- COMMIT;\n")

    print(f"✓ SQL cleanup script saved to: {sql_file}")
    print("\n⚠️  IMPORTANT: Review the SQL file before executing!")
    print("   The script includes a transaction (BEGIN/COMMIT) for safety.")

if __name__ == "__main__":
    print("\nSearching for assets in both CANNOT FIND and DEACTIVATED lists...")
    print("This will identify duplicates that should be removed from the Cannot Find list.\n")

    duplicate_bfm_numbers = find_duplicate_assets()

    if duplicate_bfm_numbers:
        print(f"\n{'='*120}")
        print(f"Found {len(duplicate_bfm_numbers)} duplicate asset(s)")
        print(f"{'='*120}\n")
        generate_cleanup_sql(duplicate_bfm_numbers)
        print("\nRECOMMENDATION: These assets are deactivated, so they should be removed")
        print("from the Cannot Find list. Use the generated SQL script to clean them up.\n")
    else:
        print("\n✓ No cleanup needed - your data is clean!\n")
