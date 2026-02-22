# Security Policy

## Supported Versions

This repository is in active development. Security fixes are applied to `main`.

## Reporting a Vulnerability

1. Do not open a public issue.
2. Send details to your internal security contact.
3. Include reproduction steps, impact, and affected paths.

## Baseline Controls

- No plaintext secrets in repository history.
- CI security gates: secret scan, dependency scan, container scan.
- Signed container artifacts (Cosign keyless) in release pipeline.
- SBOM generated for build artifacts.
