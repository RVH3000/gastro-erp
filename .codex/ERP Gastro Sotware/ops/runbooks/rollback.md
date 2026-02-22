# Rollback Runbook

## Trigger Conditions

1. Healthcheck failure on standby during production deploy.
2. Error rate > 1% for 10 minutes.
3. p95 latency > 1s for 10 minutes.
4. RKSV signing failure in critical booking flow.

## Manual Rollback

```bash
cd /opt/gastro-erp
./deploy/scripts/rollback.sh a
```

Use slot `a` or `b` based on last known stable slot.

## Validation

1. `curl -f http://localhost/api/v1/health`
2. Confirm Nginx points to expected slot (`deploy/nginx/upstream.conf`).
3. Confirm old unstable slot is stopped.
4. Open incident ticket and attach workflow logs.

## Recovery Actions

1. Revert offending commit.
2. Re-run CI PR and staging deploy.
3. Promote only after root cause is documented.

## Drill (quartalsweise)

```bash
cd /opt/gastro-erp
export DRILL_CONFIRMED=true
./deploy/scripts/rollback_drill.sh
```
