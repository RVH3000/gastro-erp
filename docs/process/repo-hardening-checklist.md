# Repo-Härtung Checkliste (GitHub)

## Repository-Einstellungen

1. `main` und Release-Branches schützen.
2. Pull-Request-Pflicht aktivieren.
3. Mindestens 1 Approval erzwingen.
4. Code-Owner-Review erzwingen.
5. Force-Push und Branch-Delete verhindern.
6. Lineare Historie aktivieren.
7. Optional: signierte Commits erzwingen.

## Pflicht-Statuschecks

Folgende Jobs müssen als required checks gesetzt werden:

1. `policy-gate`
2. `lint-type-test`
3. `security-gates`
4. `integration-contract`
5. `e2e-core-flows`

## Environments

1. `staging`
2. `production` mit required approval

## Branch Protection `main`

1. PR vor Merge erforderlich.
2. Genau 1 Approval erforderlich.
3. Status Checks müssen erfolgreich sein.

## Secret-Management

1. Secrets nur in GitHub Environments/Repository Secrets.
2. Keine Credentials im Code oder in `.env` im Repo.
3. Rotation mindestens quartalsweise.
4. Pflicht-Secrets gemäß `docs/process/github-environments-secrets.md` gesetzt.

## Automatisierungen

1. Dependabot aktiv (pip, npm, GitHub Actions).
2. `Repo Hardening Audit` Workflow mindestens wöchentlich.
3. Security-Scan-Gates blockierend im PR-Workflow.
