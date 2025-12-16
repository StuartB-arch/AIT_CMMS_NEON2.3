#!/usr/bin/env python3
"""
Diagnostic tool to check specific assets and identify issues
Run this script to diagnose why assets aren't showing up or can't be edited
"""

import sys
import os

# Add the current directory to path to import database utils
sys.path.insert(0, os.path.dirname(__file__))

from database_utils import DatabaseConnectionPool

# Database configuration
DB_CONFIG = {
    'host': 'ep-tiny-paper-ad8glt26-pooler.c-2.us-east-1.aws.neon.tech',
    'port': 5432,
    'database': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_2Nm6hyPVWiIH',
    'sslmode': 'require'
}

def diagnose_assets():
    """Check for specific assets mentioned by user"""

    search_terms = [
        "Avionic Access",
        "96007580",
        "20328877"
    ]

    try:
        # Initialize connection pool
        db_pool = DatabaseConnectionPool()
        db_pool.initialize(DB_CONFIG, min_conn=1, max_conn=2)

        print("=" * 100)
        print("ASSET DIAGNOSTIC TOOL")
        print("=" * 100)

        with db_pool.get_cursor(commit=False) as cursor:
            # First, get total count
            cursor.execute("SELECT COUNT(*) FROM equipment")
            total_count = cursor.fetchone()[0]
            print(f"\nTotal assets in equipment table: {total_count}")

            # Check each search term
            for term in search_terms:
                print(f"\n\n{'='*100}")
                print(f"Searching for: '{term}'")
                print('='*100)

                # Search in multiple fields
                cursor.execute('''
                    SELECT
                        bfm_equipment_no,
                        sap_material_no,
                        description,
                        location,
                        master_lin,
                        status,
                        weekly_pm,
                        monthly_pm,
                        six_month_pm,
                        annual_pm,
                        next_weekly_pm,
                        next_monthly_pm,
                        next_six_month_pm,
                        next_annual_pm
                    FROM equipment
                    WHERE
                        CAST(bfm_equipment_no AS TEXT) ILIKE %s OR
                        CAST(sap_material_no AS TEXT) ILIKE %s OR
                        CAST(description AS TEXT) ILIKE %s OR
                        CAST(location AS TEXT) ILIKE %s OR
                        CAST(master_lin AS TEXT) ILIKE %s
                    ORDER BY bfm_equipment_no
                ''', (f'%{term}%',) * 5)

                results = cursor.fetchall()

                if results:
                    print(f"\n✓ Found {len(results)} matching asset(s):\n")

                    for i, row in enumerate(results, 1):
                        print(f"\nAsset #{i}:")
                        print(f"  BFM Equipment No:    '{row[0]}'  (type: {type(row[0])}, length: {len(str(row[0])) if row[0] else 0})")
                        print(f"  SAP Material No:     '{row[1]}'")
                        print(f"  Description:         '{row[2]}'")
                        print(f"  Location:            '{row[3]}'")
                        print(f"  Master LIN:          '{row[4]}'")
                        print(f"  Status:              '{row[5]}'")
                        print(f"  PM Types Enabled:    Weekly={row[6]}, Monthly={row[7]}, 6-Month={row[8]}, Annual={row[9]}")
                        print(f"  Next PM Dates:")
                        print(f"    Weekly:            {row[10]}")
                        print(f"    Monthly:           {row[11]}")
                        print(f"    6-Month:           {row[12]}")
                        print(f"    Annual:            {row[13]}")

                        # Check if asset is in deactivated or cannot_find tables
                        bfm = row[0]

                        cursor.execute("SELECT COUNT(*) FROM deactivated_assets WHERE bfm_equipment_no = %s", (bfm,))
                        deact_count = cursor.fetchone()[0]

                        cursor.execute("SELECT COUNT(*) FROM cannot_find_assets WHERE bfm_equipment_no = %s", (bfm,))
                        cf_count = cursor.fetchone()[0]

                        cursor.execute("SELECT COUNT(*) FROM run_to_failure_assets WHERE bfm_equipment_no = %s", (bfm,))
                        rtf_count = cursor.fetchone()[0]

                        print(f"\n  Special Status:")
                        if deact_count > 0:
                            print(f"    ⚠ In deactivated_assets table - This asset is DEACTIVATED")
                        if cf_count > 0:
                            print(f"    ⚠ In cannot_find_assets table - This asset is marked as CANNOT FIND")
                        if rtf_count > 0:
                            print(f"    ⚠ In run_to_failure_assets table - This asset is RUN TO FAILURE")

                        if deact_count == 0 and cf_count == 0 and rtf_count == 0:
                            print(f"    ✓ No special status flags")

                        # Check for whitespace issues
                        if row[0] and (row[0] != row[0].strip()):
                            print(f"    ⚠ WARNING: BFM number has leading/trailing whitespace!")

                else:
                    print(f"\n✗ NOT FOUND in equipment table")

                    # Try exact match on BFM
                    cursor.execute("SELECT COUNT(*) FROM equipment WHERE bfm_equipment_no = %s", (term,))
                    exact_count = cursor.fetchone()[0]

                    if exact_count > 0:
                        print(f"  Note: Found {exact_count} exact match(es) for BFM '{term}'")

            # Check for common issues
            print(f"\n\n{'='*100}")
            print("COMMON ISSUES CHECK")
            print('='*100)

            # Check for NULL BFM numbers
            cursor.execute("SELECT COUNT(*) FROM equipment WHERE bfm_equipment_no IS NULL OR bfm_equipment_no = ''")
            null_bfm_count = cursor.fetchone()[0]
            if null_bfm_count > 0:
                print(f"\n⚠ Found {null_bfm_count} assets with NULL or empty BFM Equipment No")

            # Check for duplicate BFM numbers
            cursor.execute('''
                SELECT bfm_equipment_no, COUNT(*) as count
                FROM equipment
                WHERE bfm_equipment_no IS NOT NULL
                GROUP BY bfm_equipment_no
                HAVING COUNT(*) > 1
            ''')
            duplicates = cursor.fetchall()
            if duplicates:
                print(f"\n⚠ Found {len(duplicates)} duplicate BFM Equipment Numbers:")
                for bfm, count in duplicates:
                    print(f"  '{bfm}' appears {count} times")
            else:
                print(f"\n✓ No duplicate BFM numbers found")

        print(f"\n{'='*100}")
        print("DIAGNOSTIC COMPLETE")
        print('='*100)

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnose_assets()
