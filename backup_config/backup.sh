#!/bin/sh
set -e

echo "🕒 Starting backup at $(date)"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="/backups"
BACKUP_FILE="${BACKUP_DIR}/dbbackup_${TIMESTAMP}.sql"
DB_NAME="personal_finance_db"
TABLE_NAME="users"

mkdir -p "$BACKUP_DIR"

# -----------------------------
# 1. Check MySQL connectivity
# -----------------------------
if ! mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e "SELECT 1;" >/dev/null 2>&1; then
  echo "❌ MySQL not reachable. Aborting backup."
  exit 1
fi
echo "✔ MySQL reachable"

# -----------------------------
# 2. Check DB exists
# -----------------------------
DB_EXISTS=$(mysql -u root -p"$MYSQL_ROOT_PASSWORD" -N -s \
  -e "SELECT COUNT(*) FROM information_schema.schemata WHERE schema_name='${DB_NAME}';")

if [ "$DB_EXISTS" -eq 0 ]; then
  echo "⚠ Database does not exist yet. Skipping backup."
  exit 0
fi
echo "✔ Database exists"

# -----------------------------
# 3. Check table exists
# -----------------------------
TABLE_EXISTS=$(mysql -u root -p"$MYSQL_ROOT_PASSWORD" -N -s \
  -e "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='${DB_NAME}' AND table_name='${TABLE_NAME}';")

if [ "$TABLE_EXISTS" -eq 0 ]; then
  echo "⚠ Table '${TABLE_NAME}' not found. Skipping backup."
  exit 0
fi
echo "✔ Table exists"

# -----------------------------
# 4. Check table is not empty
# -----------------------------
USER_COUNT=$(mysql -u root -p"$MYSQL_ROOT_PASSWORD" -N -s \
  -e "SELECT COUNT(*) FROM ${DB_NAME}.${TABLE_NAME};")

if [ "$USER_COUNT" -eq 0 ]; then
  echo "⚠ No data found in table. Skipping backup."
  exit 0
fi
echo "✔ Found $USER_COUNT users"

# -----------------------------
# 5. Dump database
# -----------------------------
mysqldump \
  -u root \
  -p"$MYSQL_ROOT_PASSWORD" \
  --single-transaction \
  --quick \
  --routines \
  --events \
  --databases "$DB_NAME" \
  > "$BACKUP_FILE"

# -----------------------------
# 6. Compress
# -----------------------------
gzip "$BACKUP_FILE"
echo "✔ Backup created: ${BACKUP_FILE}.gz"

# -----------------------------
# 7. Protect golden backup
# -----------------------------
GOLDEN="${BACKUP_DIR}/dbbackup_GOLDEN.sql.gz"
if [ ! -f "$GOLDEN" ]; then
  cp "${BACKUP_FILE}.gz" "$GOLDEN"
  echo "⭐ Golden backup created"
fi

# -----------------------------
# 8. Retention: keep last 10
# -----------------------------
ls -t ${BACKUP_DIR}/dbbackup_*.sql.gz 2>/dev/null \
  | grep -v GOLDEN \
  | tail -n +11 \
  | xargs -r rm

echo "🧹 Old backups rotated"
echo "✅ Backup completed successfully"
