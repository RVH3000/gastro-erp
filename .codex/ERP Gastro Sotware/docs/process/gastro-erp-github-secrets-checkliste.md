# GitHub Secrets & Environments Checkliste
## Gastro-ERP (staging + production)

Stand: 22. Februar 2026

## 1. Environments anlegen

1. `staging`
2. `production`

Für `production`:

1. Required reviewers: mindestens 1 Person
2. Wait timer: 0 Minuten

## 2. Required Secrets

### Für beide Environments (`staging`, `production`)

1. `DATABASE_URL`
2. `JWT_SECRET`
3. `REDIS_URL`
4. `SMTP_HOST`
5. `SMTP_PORT`
6. `SMTP_USER`
7. `SMTP_PASSWORD`
8. `DB_PASSWORD`
9. `GRAFANA_PASSWORD`

### Deployment-spezifisch

1. `STAGING_HOST`
2. `STAGING_SSH_KEY`
3. `STAGING_BASE_URL`
4. `PROD_HOST`
5. `PROD_SSH_KEY`
6. `PROMETHEUS_URL`

### RKSV (A-Trust)

1. `ATRUST_API_KEY`
2. `ATRUST_CERT_PEM`

## 3. Optional Secrets

1. `ALERTMANAGER_SLACK_URL`

## 4. Branch Protection auf `main`

1. Require pull request before merging
2. Require approvals: `1`
3. Require status checks to pass before merging
4. Require branches to be up to date before merging
5. Disallow force push und branch deletion

## 5. Required Status Checks

1. `policy-gate`
2. `lint-type-test`
3. `security-gates`
4. `integration-contract`
5. `e2e-core-flows`

## 6. Sicherheits-Hinweise

1. Keine Secrets im Code oder in Commit-Messages.
2. `JWT_SECRET` nur mit geplanter Session-Invalidierung ändern.
3. `DB_PASSWORD` stark setzen und rotieren.
4. SSH-Key nur für `deploy`-User mit minimalen Rechten.
