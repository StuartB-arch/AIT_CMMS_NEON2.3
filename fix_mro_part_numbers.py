#!/usr/bin/env python3
"""
One-time database cleanup script to remove leading/trailing spaces from MRO part numbers.

This script will:
1. Update mro_inventory table to trim part_number field
2. Update mro_stock_transactions table to trim part_number field
3. Update cm_parts_used table to trim part_number field
4. Display before/after counts and affected records
"""

import sys
sys.path.insert(0, '/home/user/AIT_CMMS_NEON2.3')

from database_utils import db_pool

def main():
    print("=" * 80)
    print("MRO Part Number Cleanup Script")
    print("=" * 80)
    print()

    try:
        with db_pool.get_cursor(commit=False) as cursor:
            # First, check which part numbers have leading/trailing spaces
            print("1. Checking for part numbers with leading/trailing spaces...")
            print("-" * 80)

            cursor.execute("""
                SELECT part_number, name, LENGTH(part_number) as len
                FROM mro_inventory
                WHERE part_number != TRIM(part_number)
                ORDER BY part_number
            """)

            affected_parts = cursor.fetchall()

            if not affected_parts:
                print("✓ No part numbers found with leading/trailing spaces!")
                print("  Database is already clean.")
                return

            print(f"Found {len(affected_parts)} part number(s) with leading/trailing spaces:\n")
            for part in affected_parts:
                original = part['part_number']
                trimmed = original.strip()
                print(f"  '{original}' (len:{part['len']}) → '{trimmed}' (len:{len(trimmed)}) - {part['name']}")

            print()
            response = input("Do you want to proceed with cleanup? (yes/no): ").strip().lower()

            if response != 'yes':
                print("\nCleanup cancelled.")
                return

            print()
            print("2. Updating part numbers...")
            print("-" * 80)

        # Start the actual updates
        with db_pool.get_cursor(commit=True) as cursor:
            # Update mro_inventory table
            print("  Updating mro_inventory...")
            cursor.execute("""
                UPDATE mro_inventory
                SET part_number = TRIM(part_number)
                WHERE part_number != TRIM(part_number)
            """)
            mro_inv_count = cursor.rowcount
            print(f"    ✓ Updated {mro_inv_count} record(s) in mro_inventory")

            # Update mro_stock_transactions table
            print("  Updating mro_stock_transactions...")
            cursor.execute("""
                UPDATE mro_stock_transactions
                SET part_number = TRIM(part_number)
                WHERE part_number != TRIM(part_number)
            """)
            trans_count = cursor.rowcount
            print(f"    ✓ Updated {trans_count} record(s) in mro_stock_transactions")

            # Update cm_parts_used table
            print("  Updating cm_parts_used...")
            cursor.execute("""
                UPDATE cm_parts_used
                SET part_number = TRIM(part_number)
                WHERE part_number != TRIM(part_number)
            """)
            cm_count = cursor.rowcount
            print(f"    ✓ Updated {cm_count} record(s) in cm_parts_used")

        print()
        print("=" * 80)
        print("✓ Cleanup completed successfully!")
        print("=" * 80)
        print()
        print("Summary:")
        print(f"  - mro_inventory: {mro_inv_count} part numbers trimmed")
        print(f"  - mro_stock_transactions: {trans_count} part numbers trimmed")
        print(f"  - cm_parts_used: {cm_count} part numbers trimmed")
        print()
        print("All part numbers have been cleaned. Leading/trailing spaces removed.")
        print()

    except Exception as e:
        print(f"\n❌ Error during cleanup: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
