# Monitoring Stack

Start:

```bash
docker compose -f docker-compose.monitoring.yml up -d
```

Pflicht-Umgebungsvariablen:

1. `GRAFANA_PASSWORD` (optional, Default `admin`)

Enthaltene Komponenten:

1. Prometheus
2. Grafana (provisioned Dashboard)
