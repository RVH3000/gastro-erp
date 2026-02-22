# Observability Stack

## Start

```bash
cd ops/observability
docker compose -f docker-compose.monitoring.yml up -d
```

## Components

1. Prometheus (`:9090`)
2. Alertmanager (`:9093`)
3. Grafana (`:3000`)
4. Loki (`:3100`)
5. Promtail (logs collector)
6. Node Exporter (`:9100`)

## Notes

1. Set `ALERTMANAGER_SLACK_URL` and optional `ALERTMANAGER_WHATSAPP_URL` in the shell or `.env`.
2. Backend must expose `/metrics`.
3. Alert rules are in `alert-rules.yml`.
