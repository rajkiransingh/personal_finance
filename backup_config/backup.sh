#!/bin/bash
set -e

echo "Starting backup at $(date)"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="/var/lib/mysql/backups"
BACKUP_FILE="${BACKUP_DIR}/dbbackup_${TIMESTAMP}.sql"

# Ensure backup directory exists
mkdir -p $BACKUP_DIR

# Create database backup
mysqldump -u root -p$MYSQL_ROOT_PASSWORD --all-databases > $BACKUP_FILE

# Compress the backup
gzip $BACKUP_FILE

# Keep only the last 7 backups
ls -t ${BACKUP_DIR}/dbbackup_*.sql.gz | tail -n +5 | xargs rm -f

echo "Database backup completed: ${BACKUP_FILE}.gz"