#!/bin/sh

echo "Starting backup at $(date)"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="/backups"
BACKUP_FILE="${BACKUP_DIR}/dbbackup_${TIMESTAMP}.sql"

# Ensure backup directory exists
mkdir -p $BACKUP_DIR

# Create database backup
mysqldump -u root -p$MYSQL_ROOT_PASSWORD --all-databases > $BACKUP_FILE

# Compress the backup
gzip $BACKUP_FILE

# Keep only the last 4 backups (using simpler rm in BusyBox)
BACKUP_FILES=$(ls -t ${BACKUP_DIR}/dbbackup_*.sql.gz | tail -n +4)
if [ -n "$BACKUP_FILES" ]; then
  echo "Deleting old backups: $BACKUP_FILES"
  echo "$BACKUP_FILES" | xargs rm
fi

echo "Database backup completed: ${BACKUP_FILE}.gz"