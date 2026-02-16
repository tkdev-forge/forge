# Technology Decisions (Implementation Baseline)

**Status:** Approved for implementation phase (PoC → Pilot)  
**Date:** 2026-02-16  
**Scope:** `forge-framework` contracts + backend + deployment baseline

## 1) Locked versions and tooling baseline

To avoid drift during implementation, we will use the following **pinned baseline versions**.

| Area | Decision (Locked) | Source of truth |
|---|---|---|
| Solidity compiler | `0.8.24` | `contracts/foundry.toml`, `contracts/hardhat.config.js` |
| OpenZeppelin contracts | `@openzeppelin/contracts@5.0.2` | `contracts/package.json` |
| Chainlink contracts | `@chainlink/contracts@1.2.0` | `contracts/package.json` |
| Python runtime | `Python 3.11.x` (team standard; patch version pinned in container images/CI) | this document + CI/container setup |
| Database | `PostgreSQL 15` | docker compose images |
| ORM | `SQLAlchemy 2.0.35` | `backend/requirements.txt` |
| PostgreSQL driver | `psycopg2-binary 2.9.9` | `backend/requirements.txt` |
| Backend async model | **FastAPI async boundary + synchronous SQLAlchemy sessions in threadpool execution paths** | backend code structure |

### Why this is a lock (not a suggestion)

- We are in an implementation-heavy phase; changing compiler/runtime/library versions while core behavior is still moving creates avoidable debugging surface.
- These versions are already present in project config and should be treated as the compatibility contract until a deliberate upgrade ADR is approved.

## 2) Foundry + Hardhat decision

## Decision: Keep **both Foundry and Hardhat** for this project phase.

Both tools are required, but with strict separation of responsibilities:

### Foundry responsibilities (default contract engineering tool)

- Solidity unit/integration testing (`forge test`) and gas reporting.
- Scripted deployment flows for EVM targets where current Foundry scripts are maintained.
- Fast local feedback loop for contract development and regression checks.

### Hardhat responsibilities (JavaScript ecosystem integration tool)

- NPM package dependency management for Solidity libraries (`@openzeppelin`, `@chainlink`).
- JS/TS-compatible deployment/ops scripts where Node-based workflows are required.
- Tooling interoperability with existing Hardhat plugin ecosystem when needed.

### Guardrail

- **No duplicate “primary” workflows**: contract test truth lives in Foundry unless an explicit exception is documented.
- Hardhat is retained for package/deploy ecosystem compatibility, not as a second testing authority.

## 3) Rationale by decision area

### Solidity `0.8.24`

- Already aligned across Foundry and Hardhat config.
- Stable and modern compiler target with mature ecosystem support.

**Not chosen:**
- `0.8.25+` now: deferred to avoid introducing compiler-level behavior differences mid-implementation.
- Older `<0.8.20`: unnecessary loss of language/compiler improvements.

### OpenZeppelin `5.0.2` and Chainlink `1.2.0`

- Matches current contract package baseline.
- Keeps us aligned with current code and import expectations.

**Not chosen:**
- Floating semver (`^`) behavior in practice: rejected for implementation determinism.
- Immediate major/minor upgrades: deferred until core features stabilize.

### Python `3.11.x`

- Strong compatibility with FastAPI/SQLAlchemy/Web3 stack.
- Better runtime performance and typing ergonomics than 3.10 for this codebase.

**Not chosen:**
- Python 3.12 immediately: not required for current goals; defer until full dependency validation.
- Python 3.10: functional, but no upside versus 3.11 for this project.

### PostgreSQL 15

- Explicitly used in compose setup already.
- Good operational maturity and feature set for the pilot scale.

**Not chosen:**
- PostgreSQL 16 now: potential upgrade work with no immediate research benefit.
- SQLite for core paths: rejected due to concurrency/feature limitations for pilot workloads.

### SQLAlchemy 2.0.35 + psycopg2-binary 2.9.9 + sync DB access model

- Mirrors existing backend implementation pattern (`Session`, `create_engine`, sync driver).
- Minimizes migration risk while core domain logic is still under active construction.

**Not chosen:**
- `asyncpg` + SQLAlchemy async session as default today: rejected for now to avoid broad refactor cost and subtle transaction/concurrency changes during active development.
- Raw SQL-only approach: rejected due to maintainability and model consistency needs.

## 4) Upgrade/change policy (anti re-litigation rule)

A change to any locked item above requires:

1. A short ADR or equivalent decision note.
2. Impact statement (contracts, DB migrations, CI, deploy scripts, perf/risk).
3. Green test run for affected layers.
4. Rollback plan.

Without these, version/tool changes should be considered out of scope for feature PRs.

## 5) Practical implementation checklist

- Keep compiler version parity between Foundry and Hardhat.
- Keep contract package versions pinned and upgrade only via dedicated dependency PR.
- Standardize CI/runtime images to Python 3.11 patch-level pin.
- Keep backend DB stack on SQLAlchemy sync + psycopg2 until async migration is separately approved.
