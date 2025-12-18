-- ==================================================================================
-- FIND ASSETS IN BOTH 'CANNOT FIND' AND 'DEACTIVATED' LISTS
-- ==================================================================================
-- Purpose: Identify assets that appear in both cannot_find_assets and
--          deactivated_assets tables. These duplicates should be removed from
--          the Cannot Find list since they are already deactivated.
-- ==================================================================================

-- QUERY 1: Simple list of duplicate BFM numbers
-- ==================================================================================
SELECT
    cf.bfm_equipment_no as "BFM Number"
FROM cannot_find_assets cf
INNER JOIN deactivated_assets d ON cf.bfm_equipment_no = d.bfm_equipment_no
WHERE cf.status = 'Missing'
ORDER BY cf.bfm_equipment_no;


-- QUERY 2: Detailed information about duplicates
-- ==================================================================================
SELECT
    cf.bfm_equipment_no as "BFM Number",
    e.sap_material_no as "SAP Number",
    e.description as "Description",
    cf.location as "Cannot Find Location",
    cf.reported_by as "Reported By",
    cf.reported_date as "Reported Date",
    cf.status as "Cannot Find Status",
    d.deactivated_by as "Deactivated By",
    d.deactivated_date as "Deactivated Date",
    d.reason as "Deactivation Reason",
    d.status as "Deactivated Status"
FROM cannot_find_assets cf
INNER JOIN deactivated_assets d ON cf.bfm_equipment_no = d.bfm_equipment_no
LEFT JOIN equipment e ON cf.bfm_equipment_no = e.bfm_equipment_no
WHERE cf.status = 'Missing'
ORDER BY cf.bfm_equipment_no;


-- QUERY 3: Count of duplicates
-- ==================================================================================
SELECT COUNT(*) as "Total Duplicates"
FROM cannot_find_assets cf
INNER JOIN deactivated_assets d ON cf.bfm_equipment_no = d.bfm_equipment_no
WHERE cf.status = 'Missing';


-- QUERY 4: Generate DELETE statements to remove duplicates
-- ==================================================================================
-- CAUTION: Review these DELETE statements carefully before executing!
-- Consider creating a backup first:
-- CREATE TABLE cannot_find_assets_backup AS SELECT * FROM cannot_find_assets;

SELECT
    'DELETE FROM cannot_find_assets WHERE bfm_equipment_no = ''' || cf.bfm_equipment_no || ''';' as "Cleanup SQL"
FROM cannot_find_assets cf
INNER JOIN deactivated_assets d ON cf.bfm_equipment_no = d.bfm_equipment_no
WHERE cf.status = 'Missing'
ORDER BY cf.bfm_equipment_no;


-- QUERY 5: Safe cleanup using transaction
-- ==================================================================================
-- Uncomment and execute this block to safely remove duplicates:

/*
BEGIN;

-- Create backup table first
CREATE TABLE IF NOT EXISTS cannot_find_assets_backup AS
SELECT * FROM cannot_find_assets WHERE 1=0;

INSERT INTO cannot_find_assets_backup
SELECT * FROM cannot_find_assets cf
WHERE EXISTS (
    SELECT 1 FROM deactivated_assets d
    WHERE d.bfm_equipment_no = cf.bfm_equipment_no
);

-- Delete duplicates
DELETE FROM cannot_find_assets
WHERE bfm_equipment_no IN (
    SELECT cf.bfm_equipment_no
    FROM cannot_find_assets cf
    INNER JOIN deactivated_assets d ON cf.bfm_equipment_no = d.bfm_equipment_no
    WHERE cf.status = 'Missing'
);

-- Review the changes
SELECT 'Backed up and deleted ' || COUNT(*) || ' duplicate assets' as "Result"
FROM cannot_find_assets_backup;

-- If everything looks good, commit:
COMMIT;

-- If you want to undo, run instead:
-- ROLLBACK;
*/


-- QUERY 6: Verify cleanup (run after deletion)
-- ==================================================================================
-- This should return 0 rows if cleanup was successful
SELECT COUNT(*) as "Remaining Duplicates"
FROM cannot_find_assets cf
INNER JOIN deactivated_assets d ON cf.bfm_equipment_no = d.bfm_equipment_no
WHERE cf.status = 'Missing';
