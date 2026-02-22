#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="deploy/compose/docker-compose.blue-green.yml"
STATE_FILE="deploy/.active_slot"
OBSERVATION_SECONDS="${OBSERVATION_SECONDS:-300}"
MAX_ERROR_RATE="${MAX_ERROR_RATE:-0.01}"
MAX_P95_SECONDS="${MAX_P95_SECONDS:-1.0}"
PROMETHEUS_URL="${PROMETHEUS_URL:-}"

if [[ -z "${BACKEND_IMAGE_DIGEST:-}" ]]; then
  echo "BACKEND_IMAGE_DIGEST is required"
  exit 1
fi

active_slot="a"
if [[ -f "${STATE_FILE}" ]]; then
  active_slot="$(cat "${STATE_FILE}")"
fi

if [[ "${active_slot}" == "a" ]]; then
  standby_slot="b"
  standby_port="8001"
else
  standby_slot="a"
  standby_port="8000"
fi

echo "[deploy] active=${active_slot} standby=${standby_slot}"

echo "[deploy] start standby stack"
docker compose -f "${COMPOSE_FILE}" up -d "backend_${standby_slot}"

echo "[deploy] run migration before traffic switch"
docker compose -f "${COMPOSE_FILE}" run --rm migrator

echo "[deploy] wait for standby health"
for _ in {1..20}; do
  if curl -fsS "http://localhost:${standby_port}/api/v1/health" >/dev/null; then
    echo "[deploy] standby healthy"
    break
  fi
  sleep 3
done

if ! curl -fsS "http://localhost:${standby_port}/api/v1/health" >/dev/null; then
  echo "[deploy] standby health failed, keep active slot"
  exit 1
fi

echo "[deploy] explicit nginx upstream switch"
cp "deploy/nginx/upstream_${standby_slot}.conf" "deploy/nginx/upstream.conf"
docker compose -f "${COMPOSE_FILE}" exec -T nginx nginx -s reload
echo "${standby_slot}" > "${STATE_FILE}"

extract_prom_value() {
  python - "$@" <<'PY'
import json
import sys

payload = json.load(sys.stdin)
result = payload.get("data", {}).get("result", [])
if not result:
    print("nan")
    sys.exit(0)
print(result[0]["value"][1])
PY
}

check_slo() {
  if [[ -z "${PROMETHEUS_URL}" ]]; then
    echo "[deploy] PROMETHEUS_URL not set, skipping SLO query checks"
    return 0
  fi

  error_rate_json="$(curl -fsS --get "${PROMETHEUS_URL}/api/v1/query" --data-urlencode 'query=sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))')"
  p95_json="$(curl -fsS --get "${PROMETHEUS_URL}/api/v1/query" --data-urlencode 'query=histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))')"

  error_rate="$(printf '%s' "${error_rate_json}" | extract_prom_value)"
  p95="$(printf '%s' "${p95_json}" | extract_prom_value)"

  python - "${error_rate}" "${p95}" "${MAX_ERROR_RATE}" "${MAX_P95_SECONDS}" <<'PY'
import math
import sys

error_rate = float(sys.argv[1]) if sys.argv[1] != "nan" else math.nan
p95 = float(sys.argv[2]) if sys.argv[2] != "nan" else math.nan
max_error = float(sys.argv[3])
max_p95 = float(sys.argv[4])

if not math.isnan(error_rate) and error_rate > max_error:
    print(f"error-rate breach: {error_rate} > {max_error}")
    sys.exit(1)
if not math.isnan(p95) and p95 > max_p95:
    print(f"p95 breach: {p95} > {max_p95}")
    sys.exit(1)
PY
}

echo "[deploy] observation window ${OBSERVATION_SECONDS}s"
elapsed=0
while [[ "${elapsed}" -lt "${OBSERVATION_SECONDS}" ]]; do
  if ! check_slo; then
    echo "[deploy] SLO violation, rollback to slot ${active_slot}"
    ./deploy/scripts/rollback.sh "${active_slot}"
    exit 1
  fi
  sleep 30
  elapsed=$((elapsed + 30))
done

echo "[deploy] stop old slot backend_${active_slot}"
docker compose -f "${COMPOSE_FILE}" stop "backend_${active_slot}" || true

echo "[deploy] production switch completed"
