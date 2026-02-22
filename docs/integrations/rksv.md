# RKSV Integration Contract (A-Trust vorbereitet)

## Scope

Phase 1 liefert stabile API-Verträge und testbare Provider-Struktur.
Standard ist `stub`, Live-Betrieb erfolgt mit `FISCAL_PROVIDER=atrust`.

## Endpoints

- `POST /v1/integrations/fiscal/sign`
- `POST /v1/integrations/fiscal/dep-export`
- `POST /v1/integrations/fiscal/jahresbeleg`

### Dry-Run Signatur

`POST /v1/integrations/fiscal/sign?dry_run=true`

1. Baut den A-Trust Signatur-Request.
2. Validiert Request + Provider-Konfiguration.
3. Sendet keinen externen Request.

## Request Fields

- `tenant_id`
- `trace_id`
- `receipt_reference`
- `payload` (cash-register booking payload)

## Response Fields (Signatur)

- `status` (`signed` or `failed`)
- `signature_provider`
- `signature_value`
- `dep_reference`

## DEP-Export

1. Endpoint: `/v1/integrations/fiscal/dep-export`
2. Liefert `export_reference` + `dep_payload` (DEP_JSON-Vorbereitung).
3. Payload bleibt revisionssicher speicherbar/exportierbar.

## Jahresbeleg

1. Endpoint: `/v1/integrations/fiscal/jahresbeleg`
2. Liefert `receipt_reference` + `annual_receipt_payload`.
3. Ziel: Übergabe an RKSV-konformen Jahresabschlussprozess.

## Operational Rules

1. All requests must emit an audit event.
2. Critical sign failures are blocking for fiscal completion.
3. DEP references must be immutable and exportable.

## A-Trust Provider Struktur (vorbereitet)

1. `backend/app/integrations/providers/fiscal/atrust.py`
2. Factory-Auswahl über `FISCAL_PROVIDER=atrust`
3. Erforderliche Secrets:
- `ATRUST_API_KEY`
- `ATRUST_CERT_PEM`
4. Dry-Run Default: `ATRUST_DRY_RUN=true`

## Startup Fail-Fast

Wenn `APP_ENV=production` und `FISCAL_PROVIDER=atrust`, dann muss beim Start gelten:

1. `ATRUST_API_KEY` gesetzt und formatvalid.
2. `ATRUST_CERT_PEM` gesetzt und PEM-formatvalid.

Fehlt eines davon, bricht der App-Start bewusst ab.

## Provider-ready Konfiguration (jetzt bereits vorhanden)

1. `FISCAL_PROVIDER=stub` (Default)
2. `FISCAL_PROVIDER=atrust` (Live-Provider vorbereitet)
3. Provider werden über die Factory registriert:
- `backend/app/integrations/factory.py`
- `backend/app/integrations/providers/fiscal/`
