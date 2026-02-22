# Deployment Runbook

## Preconditions

1. Release image is built, signed, and has SBOM artifact.
2. Staging deployment and smoke tests passed.
3. Production approval is granted in GitHub Environment.

## Staging

1. Trigger `Deploy Staging` workflow with `image_digest`.
2. Validate `/api/v1/health`.
3. Run E2E flow:
- Wareneingang buchen
- MHD-Warnung sichtbar
- Planungskalkulation 33%
- Inventurabschluss

## Production (Blue-Green)

1. Trigger `Deploy Production` workflow with same `image_digest`.
2. Script starts standby slot and runs migration before switch.
3. Script applies explicit upstream switch (`upstream_a.conf`/`upstream_b.conf`) and reloads Nginx.
4. Observe SLO window for 300s.
5. If no SLO breach, old slot is stopped.

## Post-Deploy Checks

1. Error rate under 1%.
2. p95 below 1s.
3. RKSV signing failures at 0 in release window.
4. BMD export status endpoint healthy.

## Backup/Restore Drill (quartalsweise)

```bash
cd /opt/gastro-erp
export DATABASE_URL='postgresql://...'
./deploy/scripts/backup_restore_drill.sh
```
