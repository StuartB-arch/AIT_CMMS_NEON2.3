# ⚡ Quick Start Guide - Local PostgreSQL Migration

**Fast-track guide for experienced users. For detailed instructions, see MIGRATION_GUIDE.md**

---

## 📋 Pre-Migration Checklist

- [ ] Linux PC designated as database server
- [ ] Server IP address noted: `________________`
- [ ] Admin/sudo access confirmed
- [ ] 2GB+ free disk space

---

## 🚀 Installation (40 minutes)

### 1. Install PostgreSQL (5 min)

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install postgresql postgresql-contrib -y
sudo systemctl start postgresql && sudo systemctl enable postgresql

# Get server IP
hostname -I  # Write this down!
```

### 2. Create Database (3 min)

```bash
sudo -u postgres psql << EOF
CREATE DATABASE cmms_db;
CREATE USER cmms_user WITH ENCRYPTED PASSWORD 'YourSecurePassword123!';
GRANT ALL PRIVILEGES ON DATABASE cmms_db TO cmms_user;
\c cmms_db
GRANT ALL ON SCHEMA public TO cmms_user;
ALTER DATABASE cmms_db OWNER TO cmms_user;
EOF
```

### 3. Configure Network Access (5 min)

```bash
# Edit postgresql.conf
sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" \
    /etc/postgresql/*/main/postgresql.conf

# Edit pg_hba.conf
echo "host    all    all    192.168.0.0/16    md5" | \
    sudo tee -a /etc/postgresql/*/main/pg_hba.conf

# Firewall
sudo ufw allow 5432/tcp && sudo ufw reload

# Restart
sudo systemctl restart postgresql
```

### 4. Export from NEON (5 min)

```bash
cd /home/user/AIT_CMMS_NEON2.3/

PGPASSWORD='npg_2Nm6hyPVWiIH' pg_dump \
  -h ep-tiny-paper-ad8glt26-pooler.c-2.us-east-1.aws.neon.tech \
  -U neondb_owner -d neondb -p 5432 \
  -f neon_backup_$(date +%Y%m%d).sql
```

### 5. Import to Local (7 min)

```bash
PGPASSWORD='YourSecurePassword123!' psql \
  -h localhost -U cmms_user -d cmms_db \
  -f neon_backup_*.sql
```

### 6. Update Code (10 min)

```bash
# Edit update script
nano UPDATE_DATABASE_CONFIG.sh
# Change: SERVER_IP and DB_PASSWORD

# Run update
chmod +x UPDATE_DATABASE_CONFIG.sh
bash UPDATE_DATABASE_CONFIG.sh

# Use simplified database utils (optional)
mv database_utils.py database_utils_NEON_BACKUP.py
mv database_utils_LOCAL.py database_utils.py
```

### 7. Test (5 min)

```bash
# Edit test script
nano test_connection.py
# Update DB_CONFIG with your IP and password

# Run tests
python3 test_connection.py

# Should see: "🎉 ALL TESTS PASSED"
```

### 8. Launch Application

```bash
python3 AIT_CMMS_REV3.py
```

---

## 🔧 Quick Troubleshooting

### Can't connect from other PCs

```bash
# Check firewall
sudo ufw status
sudo netstat -tlnp | grep 5432  # Should show 0.0.0.0:5432

# If blocked by Airbus firewall, use port 443
sudo nano /etc/postgresql/*/main/postgresql.conf
# Change: port = 443
sudo systemctl restart postgresql
sudo ufw allow 443/tcp

# Update DB_CONFIG in code: 'port': 443
```

### Authentication fails

```bash
sudo -u postgres psql
ALTER USER cmms_user WITH PASSWORD 'NewPassword';
\q

# Update DB_CONFIG with new password
```

### Permission errors

```bash
sudo -u postgres psql
\c cmms_db
GRANT ALL ON SCHEMA public TO cmms_user;
GRANT ALL ON ALL TABLES IN SCHEMA public TO cmms_user;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO cmms_user;
\q
```

---

## 📊 Configuration Reference

### Files to Update (if not using script)

| File | Line | What to Change |
|------|------|----------------|
| `AIT_CMMS_REV3.py` | ~6777 | DB_CONFIG |
| `migrate_multiuser.py` | ~256 | DB_CONFIG |
| `cleanup_whitespace.py` | ~15 | DB_CONFIG |
| `diagnose_assets.py` | ~16 | DB_CONFIG |
| `fix_mro_part_numbers.py` | ~22 | DB_CONFIG |
| `analyze_duplicate_assets.py` | ~17 | DB_CONFIG |

### DB_CONFIG Template

```python
DB_CONFIG = {
    'host': '192.168.1.50',  # Your server IP
    'port': 5432,             # Or 443 if firewall requires
    'database': 'cmms_db',
    'user': 'cmms_user',
    'password': 'YourSecurePassword123!'
}
```

---

## 🎯 Verification Checklist

- [ ] PostgreSQL running: `sudo systemctl status postgresql`
- [ ] Listening on network: `sudo netstat -tlnp | grep 5432`
- [ ] Firewall open: `sudo ufw status`
- [ ] Data imported: `psql -h localhost -U cmms_user -d cmms_db -c "\dt"`
- [ ] Test script passes: `python3 test_connection.py`
- [ ] Application launches: `python3 AIT_CMMS_REV3.py`
- [ ] Can login and view equipment
- [ ] Can complete PM
- [ ] Works from multiple PCs

---

## 🔑 Important Commands

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Restart PostgreSQL
sudo systemctl restart postgresql

# View PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-*-main.log

# Connect to database
PGPASSWORD='password' psql -h localhost -U cmms_user -d cmms_db

# Backup database
pg_dump -h localhost -U cmms_user -d cmms_db -f backup.sql

# Restore database
psql -h localhost -U cmms_user -d cmms_db -f backup.sql
```

---

## 🎉 Success Indicators

✅ Test script shows "ALL TESTS PASSED"
✅ Application connects without errors
✅ No keepalive messages in console
✅ Queries respond in < 50ms (much faster than NEON)
✅ Multiple users can connect simultaneously
✅ Works offline (no internet needed)

---

## 📚 More Information

- **Full Guide:** `MIGRATION_GUIDE.md`
- **Test Script:** `test_connection.py`
- **Update Script:** `UPDATE_DATABASE_CONFIG.sh`
- **Simplified Utils:** `database_utils_LOCAL.py`

---

**Need help? Check MIGRATION_GUIDE.md for detailed troubleshooting!**
