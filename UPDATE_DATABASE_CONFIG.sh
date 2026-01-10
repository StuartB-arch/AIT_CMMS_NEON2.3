#!/bin/bash
# Script to update database configuration from NEON to local PostgreSQL
#
# BEFORE RUNNING:
# 1. Replace YOUR_SERVER_IP with your Linux server's IP address
# 2. Replace YOUR_PASSWORD with the password you created for cmms_user
#
# Usage: bash UPDATE_DATABASE_CONFIG.sh

echo "=========================================="
echo "Database Configuration Update Script"
echo "=========================================="
echo ""

# CONFIGURATION - UPDATE THESE VALUES
SERVER_IP="192.168.1.50"  # CHANGE THIS to your Linux server IP
DB_PASSWORD="YourSecurePassword123!"  # CHANGE THIS to your password

echo "Configuration:"
echo "  Server IP: $SERVER_IP"
echo "  Database: cmms_db"
echo "  User: cmms_user"
echo ""

read -p "Are these values correct? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "Please edit this script and update SERVER_IP and DB_PASSWORD"
    exit 1
fi

echo ""
echo "Creating backup of original files..."
mkdir -p ./database_config_backup_$(date +%Y%m%d_%H%M%S)
cp AIT_CMMS_REV3.py ./database_config_backup_*/
cp analyze_duplicate_assets.py ./database_config_backup_*/
cp cleanup_whitespace.py ./database_config_backup_*/
cp diagnose_assets.py ./database_config_backup_*/
cp fix_mro_part_numbers.py ./database_config_backup_*/
cp migrate_multiuser.py ./database_config_backup_*/
echo "✓ Backup created"

echo ""
echo "Updating database configurations..."

# Create the new DB_CONFIG
NEW_CONFIG="DB_CONFIG = {
    'host': '$SERVER_IP',
    'port': 5432,
    'database': 'cmms_db',
    'user': 'cmms_user',
    'password': '$DB_PASSWORD'
}"

# Function to update DB_CONFIG in a file
update_file() {
    local file=$1
    echo "  Updating $file..."

    # Use Python to do the replacement
    python3 << EOF
import re

with open('$file', 'r') as f:
    content = f.read()

# Pattern to match DB_CONFIG dictionary
pattern = r"DB_CONFIG\s*=\s*\{[^}]+\}"

# Replace with new config
new_content = re.sub(pattern, '''$NEW_CONFIG''', content)

with open('$file', 'w') as f:
    f.write(new_content)

print("    ✓ Updated")
EOF
}

# Update all files
update_file "AIT_CMMS_REV3.py"
update_file "analyze_duplicate_assets.py"
update_file "cleanup_whitespace.py"
update_file "diagnose_assets.py"
update_file "fix_mro_part_numbers.py"
update_file "migrate_multiuser.py"

echo ""
echo "=========================================="
echo "✓ Configuration update complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Review the changes in the files"
echo "2. Test the application"
echo "3. If needed, restore from backup in ./database_config_backup_*/"
echo ""
