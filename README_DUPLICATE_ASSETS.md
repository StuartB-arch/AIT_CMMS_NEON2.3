# Finding Duplicate Assets: Cannot Find vs Deactivated

## Overview

This analysis helps identify assets that appear in **BOTH** the "Cannot Find" list **AND** the "Deactivated" list. These are duplicates that should be removed from the Cannot Find list, since deactivated assets shouldn't also be marked as missing.

## Why This Matters

- **Data Integrity**: If an asset is deactivated, it has a known status and shouldn't be in the "Cannot Find" list
- **Accurate Reporting**: Duplicates skew your missing asset reports
- **Clean Data**: Removing duplicates keeps your CMMS database clean and accurate

## Tools Provided

I've created **3 different tools** for you to find these duplicates:

### 1. SQL Query File (Easiest) ✅

**File**: `find_duplicate_assets.sql`

**How to use**:
1. Open your PostgreSQL client (pgAdmin, DBeaver, or NEON SQL Editor)
2. Connect to your `neondb` database
3. Open the `find_duplicate_assets.sql` file
4. Run the queries one by one to:
   - See a list of duplicate BFM numbers
   - View detailed information about each duplicate
   - Get a count of total duplicates
   - Generate DELETE statements to clean them up

**Recommended for**: Users who prefer SQL and have database access

---

### 2. Python Analyzer Script (Recommended) ⭐

**File**: `analyze_duplicate_assets.py`

**How to use**:
```bash
python3 analyze_duplicate_assets.py
```

**What it does**:
- Connects to your NEON cloud database using the same configuration as your main CMMS app
- Analyzes both tables and finds duplicates
- Generates a detailed report file with:
  - Summary table of all duplicates
  - Full details for each duplicate asset
  - List of BFM numbers to remove
- Creates a SQL cleanup script with safe transaction handling

**Outputs**:
- `duplicate_assets_report_YYYYMMDD_HHMMSS.txt` - Full analysis report
- `cleanup_duplicate_assets_YYYYMMDD_HHMMSS.sql` - SQL script to remove duplicates

**Recommended for**: Users who want automated analysis with safety checks

---

### 3. Standalone Python Script

**File**: `find_duplicate_missing_deactivated.py`

**How to use**:
```bash
python3 find_duplicate_missing_deactivated.py
```

Similar to #2 but with slightly different output formatting. Uses the same database connection.

---

## How to Run the Analysis

### Option A: Using SQL (Simplest)

1. Log into your NEON database console at: https://console.neon.tech
2. Open the SQL Editor
3. Copy and paste queries from `find_duplicate_assets.sql`
4. Run Query 1 to see the list of duplicate BFM numbers
5. Run Query 2 for detailed information

### Option B: Using Python Script (Best)

1. Open a terminal on your computer (with internet access)
2. Navigate to this directory:
   ```bash
   cd /path/to/AIT_CMMS_NEON2.3
   ```
3. Install required library (if not already installed):
   ```bash
   pip3 install psycopg2-binary
   ```
4. Run the analyzer:
   ```bash
   python3 analyze_duplicate_assets.py
   ```
5. Review the generated report files

---

## What the Analysis Shows

The analysis will display a table like this:

```
BFM Number      SAP Number   Description                              Deactivated Date  Reason
----------------------------------------------------------------------------------------------------------------------------
BFM-001         12345678     Test Equipment 1                         2024-01-15        End of life
BFM-002         23456789     Test Equipment 2                         2024-02-20        Replaced by new model
```

Each row represents an asset that is in **BOTH** lists.

---

## How to Clean Up Duplicates

### Safe Cleanup Process:

1. **Run the analysis first** to see what will be removed
2. **Review the report** - make sure these assets should be removed from Cannot Find
3. **Backup your data** (the SQL script includes backup commands)
4. **Run the cleanup SQL script**:

   ```sql
   -- The script will include this structure:
   BEGIN;

   -- Backup
   CREATE TABLE cannot_find_assets_backup AS SELECT * FROM cannot_find_assets;

   -- Delete duplicates
   DELETE FROM cannot_find_assets WHERE bfm_equipment_no = 'BFM-001';
   DELETE FROM cannot_find_assets WHERE bfm_equipment_no = 'BFM-002';
   -- ... more deletes ...

   -- Review changes
   SELECT * FROM cannot_find_assets_backup;

   -- If everything looks good:
   COMMIT;

   -- If you want to undo:
   -- ROLLBACK;
   ```

5. **Verify the cleanup** using Query 6 from the SQL file (should return 0 duplicates)

---

## Understanding the Results

### If NO duplicates are found:
```
✓ NO DUPLICATES FOUND!
All Cannot Find assets are properly separated from Deactivated assets.
No cleanup needed - your data is clean!
```

This is good! Your data is already clean.

### If duplicates ARE found:
```
⚠ FOUND 5 DUPLICATE ASSET(S)
```

You should review and clean up these duplicates using the steps above.

---

## Database Tables Analyzed

1. **cannot_find_assets** - Assets marked as "Cannot Find" with status = 'Missing'
2. **deactivated_assets** - Assets that have been deactivated
3. **equipment** - Main equipment table (joined for SAP numbers and descriptions)

## SQL Query Logic

The core query used is:

```sql
SELECT cf.bfm_equipment_no, e.sap_material_no, e.description, ...
FROM cannot_find_assets cf
INNER JOIN deactivated_assets d ON cf.bfm_equipment_no = d.bfm_equipment_no
LEFT JOIN equipment e ON cf.bfm_equipment_no = e.bfm_equipment_no
WHERE cf.status = 'Missing'
ORDER BY cf.bfm_equipment_no;
```

This finds assets where:
- The BFM number exists in **both** cannot_find_assets **and** deactivated_assets
- The Cannot Find status is 'Missing' (not already marked as 'Found')

---

## Troubleshooting

### "No module named 'psycopg2'"
```bash
pip3 install psycopg2-binary
```

### "Connection refused" or "Network error"
- Make sure you have internet connectivity
- Verify your NEON database is running
- Check that the database credentials in the script are correct

### "Can't connect to database"
- Use the SQL file instead - run queries directly in NEON console
- Or run the Python script from a machine with internet access

---

## Files Created

1. `find_duplicate_assets.sql` - SQL queries for manual execution
2. `analyze_duplicate_assets.py` - Automated Python analyzer (uses database_utils.py)
3. `find_duplicate_missing_deactivated.py` - Standalone Python analyzer
4. `README_DUPLICATE_ASSETS.md` - This file

---

## Questions?

If you find duplicates and need help deciding whether to remove them:

1. **Review the deactivation reason** - if it's legitimately deactivated, remove it from Cannot Find
2. **Check the dates** - which action came first? Deactivated or Cannot Find?
3. **When in doubt** - keep it in Cannot Find and manually investigate

---

## Next Steps

1. Run the analysis using one of the methods above
2. Review the results
3. If duplicates are found, use the generated SQL cleanup script
4. Verify the cleanup was successful
5. Refresh your CMMS application to see the updated data

---

**Created**: 2025-12-18
**Purpose**: Identify and remove duplicate assets in Cannot Find and Deactivated lists
**Recommendation**: Run this analysis monthly to keep data clean
