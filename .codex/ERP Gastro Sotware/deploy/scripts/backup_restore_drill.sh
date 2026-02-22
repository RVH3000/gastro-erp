#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "DATABASE_URL is required"
  exit 1
fi

DRILL_DIR="${DRILL_DIR:-/tmp/gastro-erp-drill}"
mkdir -p "${DRILL_DIR}"

export BACKUP_DIR="${DRILL_DIR}/backups"
export RETENTION_DAYS="1"

echo "[drill] running backup script"
./deploy/scripts/backup.sh

latest_dump="$(ls -t "${BACKUP_DIR}"/db_*.dump | head -n 1)"
if [[ -z "${latest_dump}" ]]; then
  echo "[drill] no backup dump generated"
  exit 1
fi

echo "[drill] validating dump archive: ${latest_dump}"
pg_restore --list "${latest_dump}" >/dev/null

echo "[drill] backup/restore drill succeeded"
