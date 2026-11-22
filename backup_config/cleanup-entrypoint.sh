#!/bin/bash
set -e

# Do not wipe /var/lib/mysql here. This container mounts a persistent volume,
# and deleting its contents on every start rolls the database back to the last
# hourly backup — which silently discards account passwords and other writes.
# MySQL's own entrypoint initialises the data directory only when it is empty.
exec docker-entrypoint.sh "$@"
