-- Migration script to fix weekly PM data type mismatch
-- Converts boolean True/False values to 'X'/NULL for PM columns

BEGIN;

-- Show current state before migration
SELECT 'Current PM values sample:' as info;
SELECT DISTINCT weekly_pm, monthly_pm, six_month_pm, annual_pm
FROM equipment
LIMIT 20;

-- Count equipment with boolean True values
SELECT 'Equipment counts before migration:' as info;
SELECT
    COUNT(*) FILTER (WHERE weekly_pm::text IN ('true', 't', 'True', '1')) as weekly_true_count,
    COUNT(*) FILTER (WHERE monthly_pm::text IN ('true', 't', 'True', '1')) as monthly_true_count,
    COUNT(*) FILTER (WHERE six_month_pm::text IN ('true', 't', 'True', '1')) as six_month_true_count,
    COUNT(*) FILTER (WHERE annual_pm::text IN ('true', 't', 'True', '1')) as annual_true_count,
    COUNT(*) FILTER (WHERE weekly_pm = 'X') as weekly_x_count,
    COUNT(*) FILTER (WHERE monthly_pm = 'X') as monthly_x_count
FROM equipment;

-- Update weekly_pm: True -> 'X', False/NULL -> NULL
UPDATE equipment
SET weekly_pm = CASE
    WHEN weekly_pm::text IN ('true', 't', 'True', '1', 'X', 'x') THEN 'X'
    ELSE NULL
END
WHERE weekly_pm IS NOT NULL;

-- Update monthly_pm: True -> 'X', False/NULL -> NULL
UPDATE equipment
SET monthly_pm = CASE
    WHEN monthly_pm::text IN ('true', 't', 'True', '1', 'X', 'x') THEN 'X'
    ELSE NULL
END
WHERE monthly_pm IS NOT NULL;

-- Update six_month_pm: True -> 'X', False/NULL -> NULL
UPDATE equipment
SET six_month_pm = CASE
    WHEN six_month_pm::text IN ('true', 't', 'True', '1', 'X', 'x') THEN 'X'
    ELSE NULL
END
WHERE six_month_pm IS NOT NULL;

-- Update annual_pm: True -> 'X', False/NULL -> NULL
UPDATE equipment
SET annual_pm = CASE
    WHEN annual_pm::text IN ('true', 't', 'True', '1', 'X', 'x') THEN 'X'
    ELSE NULL
END
WHERE annual_pm IS NOT NULL;

-- Verify the changes
SELECT 'Equipment counts after migration:' as info;
SELECT
    COUNT(*) FILTER (WHERE weekly_pm = 'X') as weekly_x_count,
    COUNT(*) FILTER (WHERE monthly_pm = 'X') as monthly_x_count,
    COUNT(*) FILTER (WHERE six_month_pm = 'X') as six_month_x_count,
    COUNT(*) FILTER (WHERE annual_pm = 'X') as annual_x_count,
    COUNT(*) FILTER (WHERE weekly_pm::text IN ('true', 't', 'True', '1')) as weekly_true_remaining,
    COUNT(*) FILTER (WHERE monthly_pm::text IN ('true', 't', 'True', '1')) as monthly_true_remaining
FROM equipment;

COMMIT;

-- You can now run the application and schedule weekly PMs!
SELECT '✓ Migration completed! Your weekly PM settings have been converted to the correct format.' as status;
