# Gastro ERP Bootstrap

This repository contains the CI/CD + Ops-first bootstrap for the Gastro ERP workflow:

`Wareneingang -> MHD -> Warenstand -> (Menue + Rezeptur) -> Planung -> Kassenkalkulation -> Inventur -> Feedback`

## Key Paths

- CI/CD workflows: `.github/workflows/`
- Deploy assets: `deploy/`
- Observability: `ops/observability/`
- Monitoring stack (Prometheus/Grafana/Loki): `docker-compose.monitoring.yml` + `monitoring/`
- Runbooks: `ops/runbooks/`
- Integrations docs: `docs/integrations/`
- Supply-chain docs: `docs/security/`
- Backend APIs and adapter contracts: `backend/`

## Local Backend Run

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic -c alembic.ini upgrade head
uvicorn app.main:app --reload
```

## E2E Tests

```bash
npm ci
npx playwright install chromium
npm run test:e2e
```
