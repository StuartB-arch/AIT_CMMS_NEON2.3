-- Migration: Add deactivated_assets table
-- Run this SQL script in your PostgreSQL database

-- Create deactivated_assets table
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
);

-- Verify the table was created
SELECT 'Table created successfully!' as result
WHERE EXISTS (
    SELECT FROM information_schema.tables
    WHERE table_name = 'deactivated_assets'
);
