# Branch Protection Requirements

Apply these settings to `main` and release branches:

1. Require pull request before merge.
2. Require exactly 1 approval (minimum 1).
3. Require review from Code Owners.
4. Require status checks to pass before merge:
- `policy-gate`
- `lint-type-test`
- `security-gates`
- `integration-contract`
- `e2e-core-flows`
5. Require conversation resolution before merge.
6. Require linear history.
7. Restrict force pushes and deletion.
8. Optional hardening: require signed commits.

These controls enforce the CI/CD model and 4-eyes principle.
