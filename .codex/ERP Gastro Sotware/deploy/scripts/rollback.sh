#!/usr/bin/env bash
set -euo pipefail

TARGET_SLOT="${1:-}"
COMPOSE_FILE="deploy/compose/docker-compose.blue-green.yml"
STATE_FILE="deploy/.active_slot"

if [[ -z "${TARGET_SLOT}" ]]; then
  echo "Usage: $0 <a|b>"
  exit 1
fi

if [[ "${TARGET_SLOT}" != "a" && "${TARGET_SLOT}" != "b" ]]; then
  echo "Invalid slot '${TARGET_SLOT}', expected a or b"
  exit 1
fi

if [[ "${TARGET_SLOT}" == "a" ]]; then
  OTHER_SLOT="b"
else
  OTHER_SLOT="a"
fi

echo "[rollback] ensuring backend_${TARGET_SLOT} is running"
docker compose -f "${COMPOSE_FILE}" up -d "backend_${TARGET_SLOT}"

echo "[rollback] switching nginx upstream to slot ${TARGET_SLOT}"
cp "deploy/nginx/upstream_${TARGET_SLOT}.conf" "deploy/nginx/upstream.conf"
docker compose -f "${COMPOSE_FILE}" exec -T nginx nginx -s reload

echo "${TARGET_SLOT}" > "${STATE_FILE}"

echo "[rollback] stopping backend_${OTHER_SLOT}"
docker compose -f "${COMPOSE_FILE}" stop "backend_${OTHER_SLOT}" || true

echo "[rollback] completed"
