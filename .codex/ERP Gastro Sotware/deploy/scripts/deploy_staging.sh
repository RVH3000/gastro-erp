#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="deploy/compose/docker-compose.staging.yml"
HEALTH_URL="${STAGING_HEALTH_URL:-http://localhost:8000/api/v1/health}"

if [[ -z "${BACKEND_IMAGE_DIGEST:-}" ]]; then
  echo "BACKEND_IMAGE_DIGEST is required"
  exit 1
fi

echo "[staging] pull images"
docker compose -f "${COMPOSE_FILE}" pull

echo "[staging] run migration before service restart"
docker compose -f "${COMPOSE_FILE}" run --rm backend alembic -c alembic.ini upgrade head

echo "[staging] rolling update"
docker compose -f "${COMPOSE_FILE}" up -d --remove-orphans

echo "[staging] health check: ${HEALTH_URL}"
for _ in {1..20}; do
  if curl -fsS "${HEALTH_URL}" >/dev/null; then
    echo "[staging] healthy"
    exit 0
  fi
  sleep 3
done

echo "[staging] health check failed"
exit 1
