#!/bin/bash
# Helper script for ops to apply longctx DDL to a target sqlite (staging/production).
# Usage: ./longctx_deploy_helper.sh /path/to/target.sqlite
DB="$1"
if [ -z "$DB" ]; then
  echo "Usage: $0 /path/to/target.sqlite"
  exit 1
fi
BACKUP="${DB}.bak.$(date +%s)"
cp "$DB" "$BACKUP"
if [ $? -ne 0 ]; then
  echo "Failed to backup $DB to $BACKUP"
  exit 1
fi
sqlite3 "$DB" < library/specs/longctx_ddl.sql
if [ $? -ne 0 ]; then
  echo "DDL apply failed. Restoring backup"
  cp "$BACKUP" "$DB"
  exit 1
fi
echo "DDL applied to $DB. Backup saved at $BACKUP"
