# Monitoring Stack

Start:

```bash
docker compose -f docker-compose.monitoring.yml up -d
```

Pflicht-Umgebungsvariablen:

1. `DB_PASSWORD`
2. `GRAFANA_PASSWORD`
3. `SMTP_HOST`
4. `SMTP_PORT`
5. `SMTP_USER`
6. `SMTP_PASSWORD`
7. `ALERT_EMAIL_TO`
8. `ALERT_EMAIL_FROM` (optional, Default gesetzt)

Enthaltene Komponenten:

1. Prometheus
2. Alertmanager (E-Mail)
3. Grafana (provisioned Dashboard)
4. Loki
5. Promtail
6. postgres-exporter
