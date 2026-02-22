# Supply Chain Security Baseline

## Build Integrity

1. Build from pinned action versions.
2. Build container image in CI and push to GHCR.
3. Generate SBOM (SPDX).
4. Sign image with Cosign keyless.
5. Attach provenance attestation.

## Security Gates in PR

1. Secret scanning with gitleaks.
2. Python dependency scan with pip-audit.
3. Node dependency scan with npm audit.
4. Filesystem scan with Trivy.

## Artifact Policy

1. Deploy only immutable image digests.
2. Do not deploy `latest`.
3. Keep SBOM and provenance for every production release.

## Secrets

1. Use GitHub Secrets in phase 1.
2. Prepare OIDC federation for cloud IAM.
3. Never commit credentials.
