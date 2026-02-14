# Recommended branch protection for `main`

Require these status checks before merge:
- backend / test
- contracts / forge-test
- contracts / slither

Also enable:
- Require branches to be up to date before merging.
- Require pull request reviews before merging.
