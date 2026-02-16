# Security Design

## Purpose and Scope
This document defines the security design baseline for Forge with emphasis on:

- API-facing services and operators.
- Oracle data ingestion and publication path.
- Smart contract interactions (read/write, upgrades, and privileged actions).
- Secret and key lifecycle management.

It provides a threat model, mandatory controls, and release-gate security checks.

## System Trust Boundaries
Primary trust boundaries used for analysis:

1. **External client boundary**: Any user, bot, or integration calling the API.
2. **Service boundary**: Internal service-to-service traffic and control-plane operations.
3. **Oracle boundary**: Data fetched from external sources before canonicalization and on-chain publication.
4. **Chain boundary**: Calls to and from smart contracts, including mempool exposure and reorg effects.
5. **Secret boundary**: Materialized secrets in memory, storage, CI/CD, and operational runbooks.

## Threat Model

### Threat Model Method
The model uses an attacker-centric STRIDE-style review plus abuse cases across all trust boundaries. Priorities are assigned by:

- **Likelihood**: Low / Medium / High
- **Impact**: Low / Medium / High
- **Risk**: Derived priority to drive controls and test depth

### API Threats
| Threat | Example attack | Impact | Likelihood | Required mitigations |
|---|---|---:|---:|---|
| Broken authentication | Credential stuffing, token theft, session fixation | High | High | MFA for operators, short-lived tokens, secure session binding, anomaly detection |
| Broken authorization | Horizontal/vertical privilege escalation on resource IDs | High | Medium | Centralized policy enforcement, deny-by-default, row/resource-level checks |
| Injection | JSON/path/query injection, command injection in downstream tools | High | Medium | Strong input validation, strict parsing, allowlists, output encoding |
| Replay/idempotency abuse | Reusing valid request with same signature/token | Medium | Medium | Nonce + timestamp validation, idempotency keys, bounded replay window |
| Resource exhaustion | Bot burst, expensive query abuse, cache bypass | High | High | Layered rate limits, quotas, circuit breakers, backpressure |
| Data exfiltration | Sensitive metadata leakage via error responses/logs | High | Medium | Structured redaction, least-privilege data shaping, secure logging |

### Oracle Path Threats
| Threat | Example attack | Impact | Likelihood | Required mitigations |
|---|---|---:|---:|---|
| Source poisoning | Compromised upstream data source returns manipulated value | High | Medium | Multi-source quorum, source reputation scoring, sanity bounds |
| MITM/tampering | TLS downgrade/interception between oracle fetch and internal systems | High | Low | TLS 1.2+, certificate validation/pinning where viable, signed payload verification |
| Stale/frozen feed | Replayed old datapoint accepted as fresh | High | Medium | Freshness TTL, sequence checks, monotonic timestamp constraints |
| Oracle signer compromise | Unauthorized value signed and sent on-chain | Critical | Low-Med | HSM/KMS-backed signing, split roles, emergency signer revocation |
| Publication race/reorg risk | On-chain update reordered or invalidated in reorg | Medium | Medium | Confirmation thresholds, reorg-aware reconciliation, retry policies |

### Contract Interaction Threats
| Threat | Example attack | Impact | Likelihood | Required mitigations |
|---|---|---:|---:|---|
| Privileged function misuse | Unauthorized caller invokes admin/update function | Critical | Medium | Role-gated methods, timelocks, multisig for critical actions |
| Parameter manipulation | Malformed inputs cause unexpected state transitions | High | Medium | Contract-level require/assert checks, API-side schema validation |
| Replay/front-running | Duplicate tx or mempool-based strategy attacks | High | Medium | Nonce handling, commit-reveal where needed, slippage/guard params |
| Upgrade risk | Logic upgrade introduces storage collision or backdoor | Critical | Medium | Upgrade playbooks, storage layout diff checks, staged canary rollout |
| Event/index mismatch | Off-chain system acts on malformed/duplicate events | Medium | Medium | Deterministic event parsing, idempotent consumers, finality thresholds |

### Secret Handling Threats
| Threat | Example attack | Impact | Likelihood | Required mitigations |
|---|---|---:|---:|---|
| Secret leakage in code/logs | API keys committed or printed in logs/traces | Critical | Medium | Secret scanning, redaction middleware, pre-commit and CI checks |
| Weak key lifecycle | Long-lived static keys shared across environments | High | Medium | Rotation policy, env separation, scoped credentials |
| CI/CD exfiltration | Build pipeline token exposure via insecure steps | High | Medium | OIDC short-lived credentials, protected runners, least-privilege secrets |
| Runtime memory scraping | Secrets exposed via dumps or debug endpoints | High | Low-Med | Disable debug in prod, memory hygiene, privileged access controls |

## Required Security Controls

### 1) Authentication and Authorization Matrix
All endpoints/actions must map to explicit principals, authentication methods, and authorizations.

| Principal | AuthN requirement | AuthZ scope | Example allowed actions | Notes |
|---|---|---|---|---|
| Public client | None or anonymous token | Public-only resources | Read public metadata | No access to mutable operations |
| Registered user/client | OIDC/OAuth2 access token, short TTL | Tenant + role + resource ownership | Submit idempotent API requests | Enforce token audience and issuer |
| Service account | mTLS + signed service token | Service-to-service least privilege | Oracle ingestion, internal reads | Distinct per-service identity |
| Operator/SRE | SSO + MFA + device posture | Break-glass or operational role | Rotate keys, pause/resume jobs | Break-glass is time-bound + audited |
| Contract admin signer | Hardware-backed key + multisig policy | Contract governance methods only | Upgrade, parameter changes | Timelock and two-person review required |

**Control requirements**

- Deny-by-default policy model for every API and contract-admin action.
- Authorization decisions must be centralized or policy-as-code driven; avoid ad hoc route checks.
- Every privileged action must emit an immutable audit event.

### 2) Input Validation

- Define request schemas for every API endpoint (JSON schema/strong typed DTO).
- Reject unknown fields for privileged operations.
- Enforce bounds checks (length, numeric ranges, enum allowlists, regex constraints where appropriate).
- Canonicalize and validate oracle payload format before persistence or signing.
- For contract calls, validate arguments off-chain before transaction submission.

### 3) Anti-Replay and Idempotency

- Require request timestamp and nonce for signed/high-risk operations.
- Enforce maximum accepted clock skew and replay window.
- Persist nonce/idempotency key state with TTL and status transitions (`received` → `processing` → `completed`/`failed`).
- Ensure write APIs are idempotent by key for retried client submissions.
- For event consumers, deduplicate by `(chain_id, tx_hash, log_index)` and finality threshold.

### 4) Rate Limiting and Abuse Controls

- Implement layered limits:
  - Edge/IP-level burst and sustained thresholds.
  - Principal/tenant-level quotas.
  - Endpoint class-based budgets (e.g., expensive simulation endpoints).
- Add adaptive throttling when anomaly thresholds are crossed.
- Couple limits with meaningful error codes and retry-after headers.
- Protect downstream dependencies with queue depth guards and circuit breakers.

### 5) Key and Secret Rotation

- Maintain inventory of all secrets and signing keys with owner, scope, and expiry.
- Enforce rotation cadence:
  - API/service secrets: every 90 days or less.
  - Operator credentials: every 60–90 days according to provider policy.
  - Critical signing keys: rotate via governance runbook at defined epoch boundaries or incident trigger.
- Support dual-key overlap windows for zero-downtime rotation.
- Revoke compromised credentials immediately and trigger incident response workflow.
- Validate rotation in staging before production promotion.

## Release Gate Security Test Checklist
Every release must satisfy the following gates. “N/A” is allowed only with documented justification.

### Gate 1: Pre-merge (PR)
- [ ] Static analysis and lints pass with no new high-severity findings.
- [ ] Dependency vulnerability scan run; critical/high issues triaged or blocked.
- [ ] Secrets scan on diff and repository history for new leaks.
- [ ] API schema validation tests updated for changed endpoints.
- [ ] AuthZ unit tests cover new/modified privilege paths.

### Gate 2: Pre-release (staging)
- [ ] Integration tests for authn/authz matrix across principal types.
- [ ] Negative tests for input validation (fuzz/property tests where applicable).
- [ ] Replay/idempotency tests (duplicate request, reordered delivery, retry storms).
- [ ] Rate-limit tests (burst, sustained, and multi-tenant fairness).
- [ ] Oracle freshness tests (stale/replayed data rejected).
- [ ] Contract interaction tests for role gating and failure-path safety.

### Gate 3: Pre-production approval
- [ ] Threat model reviewed for changed architecture or trust boundary.
- [ ] Key/secret inventory reviewed; required rotations completed or scheduled.
- [ ] Operational runbooks verified (incident response, key revoke/rollover, pause procedures).
- [ ] Security sign-off completed by designated reviewer(s).

### Gate 4: Post-deploy verification
- [ ] Audit logs confirm expected privileged actions only.
- [ ] Alerting and dashboards show normal auth failures, rate-limit hits, and oracle freshness.
- [ ] Canary monitoring confirms no abnormal replay, error, or gas/cost spikes.
- [ ] Rollback readiness validated during observation window.

## Evidence and Auditability Requirements
For each gate, maintain evidence artifacts:

- CI links for static analysis, dependency scans, secret scans.
- Test reports for authn/authz, replay/idempotency, and rate limiting.
- Change ticket references for key rotations and signer policy updates.
- Security approval record with date, approver, and release identifier.

Retention period should follow organizational policy and any applicable regulatory obligations.

## Ownership and Review Cadence

- **Primary owner**: Security Engineering.
- **Contributors**: API, oracle, and smart-contract maintainers; DevOps/SRE.
- **Review cadence**: At least quarterly and on any material architecture, dependency, or governance change.
