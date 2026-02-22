#!/usr/bin/env bash
set -euo pipefail

if [[ "${DRILL_CONFIRMED:-false}" != "true" ]]; then
  echo "Set DRILL_CONFIRMED=true to run rollback drill."
  exit 1
fi

STATE_FILE="deploy/.active_slot"
HEALTH_URL="${HEALTH_URL:-http://localhost/api/v1/health}"

if [[ -f "${STATE_FILE}" ]]; then
  active_slot="$(cat "${STATE_FILE}")"
else
  active_slot="a"
fi

if [[ "${active_slot}" == "a" ]]; then
  target_slot="b"
else
  target_slot="a"
fi

echo "[drill] active slot=${active_slot}, switching to ${target_slot}"
./deploy/scripts/rollback.sh "${target_slot}"

echo "[drill] validating health after first switch"
curl -fsS "${HEALTH_URL}" >/dev/null

echo "[drill] switching back to original slot ${active_slot}"
./deploy/scripts/rollback.sh "${active_slot}"

echo "[drill] validating health after rollback"
curl -fsS "${HEALTH_URL}" >/dev/null

echo "[drill] rollback drill succeeded"
