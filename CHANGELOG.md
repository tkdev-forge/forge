# Changelog

## [Unreleased]

### Added
- Foundry setup with `ForgeREP.t.sol` coverage-oriented tests and `DeployForgeREP.s.sol` deployment script.
- Backend tests for economy and governance modules with pytest + coverage integration.
- CI workflows for backend checks, Foundry tests, and Slither (high severity fail gate).
- Dependabot configuration for pip, npm, and GitHub Actions dependencies.
- Production compose file with Docker secrets and multi-stage backend build.

### Changed
- `ForgeREP` now uses `AccessControl` REP manager roles and applies a 50% maximum decay cap.
- `M2MEscrow` now includes `ReentrancyGuard` protection for trade execution.
- FastAPI app now has JWT auth support, REP-tier gating, SlowAPI rate limits, and observability endpoints.
- Database module now centralizes parameterized SQL execution helper to prevent SQL injection patterns.
