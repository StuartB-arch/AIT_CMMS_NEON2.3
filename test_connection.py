#!/usr/bin/env python3
"""
PostgreSQL Connection Test Script
Tests connectivity to your local PostgreSQL server

Usage:
    python3 test_connection.py
"""

import psycopg2
from psycopg2 import extras
import sys

# ============================================
# CONFIGURATION - UPDATE THESE VALUES
# ============================================
DB_CONFIG = {
    'host': '192.168.1.50',  # CHANGE THIS to your Linux server IP
    'port': 5432,             # Use 5432 or 443 if you configured alternative port
    'database': 'cmms_db',
    'user': 'cmms_user',
    'password': 'YourSecurePassword123!'  # CHANGE THIS to your password
}

# ============================================
# TEST FUNCTIONS
# ============================================

def test_basic_connection():
    """Test basic database connection"""
    print("\n" + "="*60)
    print("TEST 1: Basic Connection")
    print("="*60)

    try:
        print(f"Connecting to {DB_CONFIG['host']}:{DB_CONFIG['port']}...")
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            connect_timeout=10
        )

        print("✅ Connection successful!")

        # Test a simple query
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ PostgreSQL version: {version.split(',')[0]}")

        cursor.close()
        conn.close()
        return True

    except psycopg2.OperationalError as e:
        print(f"❌ Connection failed: {e}")
        print("\nPossible issues:")
        print("  - PostgreSQL not running on server")
        print("  - Firewall blocking port", DB_CONFIG['port'])
        print("  - Incorrect IP address or password")
        print("  - pg_hba.conf not configured for network access")
        return False

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_tables_exist():
    """Test that CMMS tables exist"""
    print("\n" + "="*60)
    print("TEST 2: Database Tables")
    print("="*60)

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)

        # Get list of tables
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)

        tables = [row['table_name'] for row in cursor.fetchall()]

        print(f"✅ Found {len(tables)} tables:")
        for table in tables:
            print(f"   - {table}")

        # Check for expected tables
        expected_tables = [
            'equipment', 'users', 'corrective_maintenance',
            'pm_completions', 'parts_inventory'
        ]

        missing_tables = [t for t in expected_tables if t not in tables]
        if missing_tables:
            print(f"\n⚠️  Warning: Expected tables not found: {missing_tables}")
            print("   (Data import may not be complete)")
        else:
            print("\n✅ All expected tables found!")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"❌ Error checking tables: {e}")
        return False


def test_data_counts():
    """Test that tables have data"""
    print("\n" + "="*60)
    print("TEST 3: Data Counts")
    print("="*60)

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)

        # Check row counts in main tables
        tables_to_check = [
            'equipment',
            'users',
            'corrective_maintenance',
            'pm_completions',
            'parts_inventory',
            'audit_log'
        ]

        for table in tables_to_check:
            try:
                cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                count = cursor.fetchone()['count']
                print(f"   {table:.<40} {count:>6} rows")
            except psycopg2.Error:
                print(f"   {table:.<40} (table not found)")

        print("\n✅ Data count check complete!")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"❌ Error checking data: {e}")
        return False


def test_write_operation():
    """Test write operation (insert/delete)"""
    print("\n" + "="*60)
    print("TEST 4: Write Operations")
    print("="*60)

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Try to create and drop a test table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS _connection_test (
                id SERIAL PRIMARY KEY,
                test_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            INSERT INTO _connection_test (test_data)
            VALUES ('Connection test successful')
            RETURNING id
        """)

        test_id = cursor.fetchone()[0]
        print(f"✅ INSERT successful (test record id: {test_id})")

        cursor.execute("DELETE FROM _connection_test WHERE id = %s", (test_id,))
        print(f"✅ DELETE successful")

        cursor.execute("DROP TABLE _connection_test")
        print(f"✅ DROP TABLE successful")

        conn.commit()
        print("\n✅ Write operations working correctly!")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"❌ Error testing write operations: {e}")
        try:
            conn.rollback()
        except:
            pass
        return False


def test_concurrent_connections():
    """Test multiple simultaneous connections"""
    print("\n" + "="*60)
    print("TEST 5: Concurrent Connections")
    print("="*60)

    try:
        connections = []

        # Open 5 connections simultaneously
        for i in range(5):
            conn = psycopg2.connect(**DB_CONFIG)
            connections.append(conn)
            print(f"✅ Connection {i+1}/5 established")

        # Test a query on each
        for i, conn in enumerate(connections):
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            print(f"✅ Query {i+1}/5 successful")

        # Close all
        for conn in connections:
            conn.close()

        print("\n✅ Concurrent connections working correctly!")
        return True

    except Exception as e:
        print(f"❌ Error testing concurrent connections: {e}")
        return False


def run_all_tests():
    """Run all connection tests"""
    print("\n" + "="*60)
    print("   CMMS PostgreSQL Connection Test")
    print("="*60)
    print(f"\nTesting connection to:")
    print(f"  Host:     {DB_CONFIG['host']}")
    print(f"  Port:     {DB_CONFIG['port']}")
    print(f"  Database: {DB_CONFIG['database']}")
    print(f"  User:     {DB_CONFIG['user']}")

    # Run tests
    results = []

    results.append(("Basic Connection", test_basic_connection()))

    if results[0][1]:  # Only continue if basic connection works
        results.append(("Tables Exist", test_tables_exist()))
        results.append(("Data Counts", test_data_counts()))
        results.append(("Write Operations", test_write_operation()))
        results.append(("Concurrent Connections", test_concurrent_connections()))

    # Print summary
    print("\n" + "="*60)
    print("   TEST SUMMARY")
    print("="*60)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:.<45} {status}")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    print("\n" + "="*60)
    if passed == total:
        print(f"🎉 ALL TESTS PASSED ({passed}/{total})")
        print("="*60)
        print("\n✅ Your PostgreSQL database is ready to use!")
        print("✅ You can now update your application configuration.")
        return 0
    else:
        print(f"⚠️  SOME TESTS FAILED ({passed}/{total} passed)")
        print("="*60)
        print("\n❌ Please fix the issues above before proceeding.")
        print("\nCommon solutions:")
        print("  1. Check PostgreSQL is running: sudo systemctl status postgresql")
        print("  2. Check firewall: sudo ufw status")
        print("  3. Check pg_hba.conf allows network connections")
        print("  4. Verify postgresql.conf has listen_addresses = '*'")
        print("  5. Restart PostgreSQL: sudo systemctl restart postgresql")
        return 1


if __name__ == "__main__":
    try:
        exit_code = run_all_tests()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
