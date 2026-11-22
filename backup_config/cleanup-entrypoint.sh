#!/bin/bash
set -e

# IMPORTANT (2026-11-22): this entrypoint used to run `rm -rf /var/lib/mysql/*`
# on every container start, which destroyed the entire finance database.
# That line has been removed. Data lives in the external named volume
# personal_finance_data_volume and must survive container restarts.
#
# Backups are still taken hourly by Ofelia -> /backups (host bind mount).

exec docker-entrypoint.sh "$@"
