#!/bin/bash
set -e

# Cleanup the MySQL data directory
echo "Cleaning up /var/lib/mysql..."
rm -rf /var/lib/mysql/*

# Start MySQL
exec docker-entrypoint.sh "$@"
