# BMD Export Contract (optional)

Diese Integration ist standardmäßig deaktiviert.
Aktivierung nur bei explizitem Wunsch über `ENABLE_BMD_INTEGRATION=true`.

## Endpoints

- `POST /v1/integrations/accounting/exports/bmd`
- `GET /v1/integrations/accounting/exports/{id}`

## Behavior

1. Export start endpoint returns `export_id`.
2. Status endpoint is idempotent and tracks lifecycle (`queued`, `running`, `completed`, `failed`).
3. Completed status returns artifact URL.
4. Wenn deaktiviert: Endpoint liefert `503`.

## Data Requirements

1. Export includes only tax-relevant booking records.
2. Every exported row references source booking IDs.
3. Export jobs must be idempotent per tenant and period.

## Retry Policy

1. Retry transient failures with exponential backoff.
2. Keep failed jobs queryable for incident analysis.

## Next Step

1. Wire concrete `AccountingExportAdapter` for real BMD target format.
2. Add checksum and signed export manifest.

## Provider-ready Konfiguration (jetzt bereits vorhanden)

1. `ACCOUNTING_PROVIDER=stub` (Default)
2. `ENABLE_BMD_INTEGRATION=false` (Default)
3. Künftige Provider werden über die Factory registriert:
- `backend/app/integrations/factory.py`
- `backend/app/integrations/providers/accounting/`
