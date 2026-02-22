#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-/var/backups/gastro-erp}"
RETENTION_DAYS="${RETENTION_DAYS:-7}"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"

mkdir -p "${BACKUP_DIR}"

if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "DATABASE_URL is required"
  exit 1
fi

echo "[backup] creating postgres dump"
pg_dump "${DATABASE_URL}" -F c -f "${BACKUP_DIR}/db_${TIMESTAMP}.dump"

echo "[backup] pruning files older than ${RETENTION_DAYS} days"
find "${BACKUP_DIR}" -type f -name '*.dump' -mtime "+${RETENTION_DAYS}" -delete

echo "[backup] done"
