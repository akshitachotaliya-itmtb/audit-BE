# 🔄 Migration Guide: Integer IDs → UUID

## Overview

If you have an existing database with integer-based IDs, this guide will help you migrate to the corrected UUID-based schema.

---

## ⚠️ Pre-Migration Checklist

- [ ] Backup your current database
- [ ] Document all existing data and relationships
- [ ] Test migration on a copy of the database first
- [ ] Ensure no active users during migration
- [ ] Have rollback plan ready

---

## 🎯 Migration Strategy

### Option 1: Fresh Start (Recommended for Development)

**Best for:** New projects, development environments, or when existing data is minimal

1. **Drop existing database**
   ```sql
   DROP DATABASE IF EXISTS internal_audit_be;
   CREATE DATABASE internal_audit_be;
   USE internal_audit_be;
   ```

2. **Run corrected DDL**
   ```sql
   SOURCE ddl.sql;
   ```

3. **Load master data**
   ```sql
   SOURCE seed_corrected.sql;
   ```

4. **Manually re-enter any critical transactional data**

---

### Option 2: Data Migration (For Production with Existing Data)

**Best for:** Production environments with valuable existing data

#### Step 1: Create Backup
```bash
mysqldump -u root -p internal_audit_be > backup_$(date +%Y%m%d_%H%M%S).sql
```

#### Step 2: Create Mapping Tables

Create temporary tables to map old integer IDs to new UUIDs:

```sql
-- Create mapping tables
CREATE TABLE IF NOT EXISTS migration_company_map (
  old_id INT,
  new_id CHAR(36),
  PRIMARY KEY (old_id),
  INDEX (new_id)
);

CREATE TABLE IF NOT EXISTS migration_entity_type_map (
  old_id INT,
  new_id CHAR(36),
  PRIMARY KEY (old_id)
);

CREATE TABLE IF NOT EXISTS migration_country_map (
  old_id INT,
  new_id CHAR(36),
  PRIMARY KEY (old_id)
);

-- Add similar mapping tables for all master data types
```

#### Step 3: Export Existing Data
```sql
-- Export company data
SELECT 
  company_id,
  legal_name,
  display_name,
  entity_type_id,
  country_id,
  registered_address,
  operational_hq_address,
  is_part_of_group,
  parent_group_id,
  status,
  created_by
INTO OUTFILE '/tmp/company_export.csv'
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
FROM company_master;

-- Repeat for other tables
```

#### Step 4: Create New Schema
```sql
-- Rename old database
RENAME DATABASE internal_audit_be TO internal_audit_be_old;

-- Create new database
CREATE DATABASE internal_audit_be;
USE internal_audit_be;

-- Run new DDL
SOURCE ddl.sql;

-- Load master data with UUIDs
SOURCE seed_corrected.sql;
```

#### Step 5: Populate Mapping Tables

```sql
-- For master data that was re-inserted via seed_corrected.sql,
-- map old IDs to new UUIDs based on unique identifiers

-- Example: Map entity types by name
INSERT INTO migration_entity_type_map (old_id, new_id)
SELECT 
  old.entity_type_id AS old_id,
  new.entity_type_id AS new_id
FROM internal_audit_be_old.entity_type_master old
JOIN internal_audit_be.entity_type_master new ON old.name = new.name;

-- Example: Map countries by country_code
INSERT INTO migration_country_map (old_id, new_id)
SELECT 
  old.country_id AS old_id,
  new.country_id AS new_id
FROM internal_audit_be_old.country_master old
JOIN internal_audit_be.country_master new ON old.country_code = new.country_code;
```

#### Step 6: Migrate Transactional Data

```sql
-- Migrate companies
INSERT INTO internal_audit_be.company_master (
  company_id,
  legal_name,
  display_name,
  entity_type_id,
  country_id,
  registered_address,
  operational_hq_address,
  is_part_of_group,
  parent_group_id,
  status,
  created_by,
  created_at,
  updated_at
)
SELECT 
  UUID() AS company_id,
  old.legal_name,
  old.display_name,
  COALESCE(et_map.new_id, UUID()) AS entity_type_id,
  COALESCE(c_map.new_id, UUID()) AS country_id,
  old.registered_address,
  old.operational_hq_address,
  old.is_part_of_group,
  NULL AS parent_group_id,  -- Will update in next step
  old.status,
  UUID() AS created_by,  -- Placeholder user_id
  old.created_at,
  old.updated_at
FROM internal_audit_be_old.company_master old
LEFT JOIN migration_entity_type_map et_map ON old.entity_type_id = et_map.old_id
LEFT JOIN migration_country_map c_map ON old.country_id = c_map.old_id;

-- Store company ID mappings
INSERT INTO migration_company_map (old_id, new_id)
SELECT 
  old.company_id AS old_id,
  new.company_id AS new_id
FROM internal_audit_be_old.company_master old
JOIN internal_audit_be.company_master new 
  ON old.legal_name = new.legal_name 
  AND old.cin = new.cin;

-- Migrate regulatory data
INSERT INTO internal_audit_be.regulatory_master (
  registration_id,
  company_id,
  cin,
  pan,
  lei,
  listed_status,
  exchange_list,
  ticker_symbol,
  country_id
)
SELECT 
  UUID() AS registration_id,
  c_map.new_id AS company_id,
  old.cin,
  old.pan,
  old.lei,
  old.listed_status,
  old.exchange_list,
  old.ticker_symbol,
  COALESCE(country_map.new_id, UUID()) AS country_id
FROM internal_audit_be_old.regulatory_master old
JOIN migration_company_map c_map ON old.company_id = c_map.old_id
LEFT JOIN migration_country_map country_map ON old.country_id = country_map.old_id;

-- Continue for all other tables...
```

#### Step 7: Verify Migration

```sql
-- Check record counts
SELECT 'Company Master' as table_name,
  (SELECT COUNT(*) FROM internal_audit_be_old.company_master) AS old_count,
  (SELECT COUNT(*) FROM internal_audit_be.company_master) AS new_count;

SELECT 'Regulatory Master' as table_name,
  (SELECT COUNT(*) FROM internal_audit_be_old.regulatory_master) AS old_count,
  (SELECT COUNT(*) FROM internal_audit_be.regulatory_master) AS new_count;

-- Verify UUID format
SELECT company_id, LENGTH(company_id) as len
FROM company_master
WHERE LENGTH(company_id) != 36;
-- Should return 0 rows

-- Verify foreign keys
SELECT cm.legal_name
FROM company_master cm
LEFT JOIN entity_type_master et ON cm.entity_type_id = et.entity_type_id
WHERE et.entity_type_id IS NULL;
-- Should return 0 rows
```

#### Step 8: Cleanup

```sql
-- Once verified, drop old database
-- DROP DATABASE internal_audit_be_old;

-- Drop mapping tables
DROP TABLE migration_company_map;
DROP TABLE migration_entity_type_map;
DROP TABLE migration_country_map;
```

---

## 🔧 Automated Migration Script

Here's a bash script to automate the migration:

```bash
#!/bin/bash
# migrate_to_uuid.sh

set -e  # Exit on error

DB_NAME="internal_audit_be"
DB_USER="root"
DB_PASS="your_password"
BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "=== Starting Migration to UUID Schema ==="

# 1. Create backup directory
mkdir -p "$BACKUP_DIR"

# 2. Backup existing database
echo "Creating backup..."
mysqldump -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" > "$BACKUP_DIR/backup_$TIMESTAMP.sql"
echo "✓ Backup created: $BACKUP_DIR/backup_$TIMESTAMP.sql"

# 3. Export data
echo "Exporting existing data..."
mysql -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" <<EOF
SELECT * INTO OUTFILE '/tmp/company_export_$TIMESTAMP.csv'
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
FROM company_master;
EOF
echo "✓ Data exported"

# 4. Rename old database
echo "Renaming old database..."
mysql -u "$DB_USER" -p"$DB_PASS" -e "CREATE DATABASE ${DB_NAME}_old_$TIMESTAMP;"
mysql -u "$DB_USER" -p"$DB_PASS" -e "
  CREATE DATABASE IF NOT EXISTS ${DB_NAME}_old_$TIMESTAMP;
  -- Manual steps required for MySQL < 8.0
"
echo "⚠ Manual step required: Dump and restore to ${DB_NAME}_old_$TIMESTAMP"

# 5. Create new schema
echo "Creating new schema..."
mysql -u "$DB_USER" -p"$DB_PASS" -e "DROP DATABASE IF EXISTS $DB_NAME;"
mysql -u "$DB_USER" -p"$DB_PASS" -e "CREATE DATABASE $DB_NAME;"
mysql -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" < ddl.sql
echo "✓ New schema created"

# 6. Load master data
echo "Loading master data..."
mysql -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" < seed_corrected.sql
echo "✓ Master data loaded"

# 7. Migrate transactional data
echo "Migrating transactional data..."
# Add your migration SQL here
echo "⚠ Manual migration required - see migration guide"

echo "=== Migration Complete ==="
echo "Backup location: $BACKUP_DIR/backup_$TIMESTAMP.sql"
echo "Please verify data and test thoroughly before going live"
```

Make executable:
```bash
chmod +x migrate_to_uuid.sh
./migrate_to_uuid.sh
```

---

## 📝 Post-Migration Tasks

### 1. Update Application Code
- ✅ Deploy updated codebase with UUID types
- ✅ Update any hardcoded ID values
- ✅ Clear application caches

### 2. Update API Clients
- ✅ Notify frontend developers of breaking changes
- ✅ Update API documentation
- ✅ Provide migration timeline

### 3. Testing
```bash
# Test company creation
curl -X POST http://localhost:8000/api/company-create \
  -H "Authorization: Bearer token" \
  -H "Content-Type: application/json" \
  -d '{
    "legal_name": "Migration Test Co",
    "entity_type_id": "<UUID_from_master>",
    "country_id": "<UUID_from_master>",
    "registered_address": "Test Address"
  }'

# Verify response contains UUID
# Expected: {"company_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"}
```

### 4. Monitor
- Check application logs for errors
- Monitor database performance
- Verify all foreign key relationships
- Check for null or invalid UUIDs

---

## 🚨 Rollback Plan

If migration fails:

```bash
# 1. Stop application
systemctl stop internal-audit-api

# 2. Drop new database
mysql -u root -p -e "DROP DATABASE internal_audit_be;"

# 3. Restore from backup
mysql -u root -p -e "CREATE DATABASE internal_audit_be;"
mysql -u root -p internal_audit_be < backups/backup_TIMESTAMP.sql

# 4. Revert application code
git checkout main  # or your stable branch

# 5. Restart application
systemctl start internal-audit-api
```

---

## ✅ Migration Checklist

**Pre-Migration:**
- [ ] Full database backup created
- [ ] Migration tested on staging/development
- [ ] Downtime window scheduled and communicated
- [ ] Rollback plan documented and tested
- [ ] All stakeholders notified

**During Migration:**
- [ ] Application stopped
- [ ] Database backup verified
- [ ] Old data exported
- [ ] New schema created
- [ ] Master data loaded
- [ ] Transactional data migrated
- [ ] Foreign key relationships verified
- [ ] Data counts match old database

**Post-Migration:**
- [ ] Updated application deployed
- [ ] API endpoints tested
- [ ] Data integrity verified
- [ ] Performance monitoring enabled
- [ ] API documentation updated
- [ ] Team trained on new UUID format

---

## 📞 Support

If you encounter issues during migration:

1. **Check logs:**
   ```bash
   tail -f /var/log/mysql/error.log
   tail -f /var/log/internal-audit-be/app.log
   ```

2. **Verify schema:**
   ```sql
   DESCRIBE company_master;
   SHOW CREATE TABLE company_master;
   ```

3. **Rollback if necessary** (see Rollback Plan above)

---

**Last Updated:** 2026-02-09  
**Migration Script Version:** 1.0
