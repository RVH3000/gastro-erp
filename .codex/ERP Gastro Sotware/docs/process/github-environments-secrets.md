# GitHub Environments und Secrets

## Environments

1. `staging`
2. `production`

## Pflicht-Secrets (beide Environments)

1. `DATABASE_URL`
2. `JWT_SECRET`
3. `REDIS_URL`
4. `SMTP_HOST`
5. `SMTP_PORT`
6. `SMTP_USER`
7. `SMTP_PASSWORD`
8. `DB_PASSWORD`
9. `GRAFANA_PASSWORD`

## Environment-spezifische Deploy-Secrets

### staging

1. `STAGING_HOST`
2. `STAGING_SSH_KEY`
3. `STAGING_BASE_URL`

### production

1. `PROD_HOST`
2. `PROD_SSH_KEY`
3. `PROMETHEUS_URL`

## RKSV (A-Trust) Secrets

1. `ATRUST_API_KEY`
2. `ATRUST_CERT_PEM`

## Optional

1. `ALERTMANAGER_SLACK_URL`
2. `OIDC_AWS_ROLE_ARN`
3. `OIDC_AZURE_CLIENT_ID`
4. `OIDC_AZURE_TENANT_ID`
5. `OIDC_AZURE_SUBSCRIPTION_ID`

## Repository Variables (non-secret)

1. `FISCAL_PROVIDER` (`stub` default, `atrust` für Live)
2. `ENABLE_BMD_INTEGRATION` (`false` default)

## Freigaben

1. `production` mit mindestens 1 Required Reviewer.
2. Deployments nur über signierte Image-Digests.
