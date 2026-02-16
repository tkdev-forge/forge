# Deployment Runbook

## Purpose and Scope
This runbook defines standardized deployment, promotion, monitoring, backup/restore, rollback, and secret-rotation procedures for the FORGE platform across **dev**, **staging**, and **production** environments.

## Roles and Responsibilities
- **Release Engineer (on-call):** executes deployment and rollback commands, validates health checks.
- **Service Owner:** confirms application-level readiness and approves promotion.
- **Database Owner:** validates backup integrity and leads restore operations if needed.
- **Security Owner:** leads emergency secret rotation and post-incident hardening.

## Environment Topology
- **dev**
  - Fast iteration environment.
  - Auto-deploys from `main` after CI success.
  - Uses synthetic/test data and lower resource profiles.
- **staging**
  - Production-like environment for pre-release validation.
  - Receives release candidates only.
  - Uses sanitized production snapshots where allowed.
- **prod**
  - Customer-facing environment.
  - Manual promotion only.
  - Strict change windows and approval controls.

---

## Deployment Process by Environment

### 1) Development Deployment (dev)
1. Merge feature/fix branch to `main`.
2. Ensure CI pipeline passes (unit/integration/security checks).
3. Trigger or wait for dev auto-deploy.
4. Run post-deploy smoke tests:
   - `GET /health/live`
   - `GET /health/ready`
   - a basic authenticated API transaction.
5. Verify logs and error rates for 15 minutes.
6. Mark build as "dev-validated" in release notes.

**Dev promotion gate to staging candidate:**
- CI green.
- No active Sev-1/Sev-2 incidents.
- Smoke tests pass.
- Error rate below defined threshold (see Metrics & Alerts).

### 2) Staging Deployment
1. Create and tag release candidate: `vX.Y.Z-rc.N`.
2. Deploy candidate artifact/image to staging.
3. Run database migrations in staged mode (non-destructive first).
4. Execute full validation suite:
   - API integration tests.
   - end-to-end user workflow tests.
   - migration verification and backward-compatibility checks.
5. Execute performance baseline run (load profile matching expected production p50 traffic).
6. Observe key metrics for at least 30 minutes.
7. Record deployment result and go/no-go decision.

**Staging promotion gate to production:**
- Release candidate tag signed and immutable.
- All automated tests pass.
- Performance baseline within ±10% of target latency and throughput.
- Zero open critical vulnerabilities from latest security scan.
- Product + Service Owner approval.

### 3) Production Deployment
1. Confirm approved change window and incident-free status.
2. Announce deployment start in incident/release channel.
3. Verify latest successful PostgreSQL backup exists (<24h old, restorable).
4. Deploy using progressive strategy:
   - canary (5%),
   - ramp (25%),
   - full rollout (100%) after each gate passes.
5. At each phase, validate:
   - readiness/liveness,
   - error budget burn,
   - latency and saturation.
6. If all gates pass, complete rollout and publish release confirmation.
7. Run post-deploy monitoring at elevated watch for 60 minutes.

**Production release completion criteria:**
- Canary/ramp/full phases each pass health gates.
- No rollback triggers met.
- No sustained alert at warning/critical threshold for 30 minutes after full rollout.

---

## Promotion Criteria Summary

| Criterion | dev → staging | staging → prod |
|---|---|---|
| CI status | Required green | Required green |
| Smoke tests | Required | Required |
| Integration/E2E | Optional for early dev, required for candidate | Required |
| Performance baseline | Recommended | Required |
| Security scan | Recommended | Required, no critical findings |
| Manual approvals | Service Owner | Service Owner + Product/Operations |

---

## Health Checks

### Required Endpoints
- **Liveness:** `GET /health/live`
  - Purpose: process is running.
  - Failure action: restart pod/task.
- **Readiness:** `GET /health/ready`
  - Purpose: dependency readiness (DB, cache, queue, external APIs where applicable).
  - Failure action: remove instance from load balancer and investigate.
- **Startup (if supported):** `GET /health/startup`
  - Purpose: initialization complete.

### Health Check Acceptance
- 99%+ success rate in rolling 5-minute window during rollout.
- p95 health endpoint latency < 250ms.
- No dependency timeout spikes above baseline + 20%.

---

## Key Metrics and SLO-Aligned Targets

### Application Metrics
- Request rate (RPS)
- Error rate (% 5xx + domain failures)
- Latency p50/p95/p99
- Queue depth and consumer lag
- Background job success/failure counts

### Infrastructure Metrics
- CPU utilization
- Memory working set / OOM kills
- Disk I/O latency and saturation
- Network retransmits/timeouts

### Database Metrics (PostgreSQL)
- Connection utilization
- Slow query count (>1s)
- Replication lag
- Deadlock count
- WAL growth and checkpoint duration

### Suggested SLO Targets
- Availability: **99.9% monthly**
- API p95 latency: **< 400ms** for core endpoints
- Error rate: **< 1%** steady state

---

## Alert Rules

### Warning Alerts (investigate)
- Error rate > 1% for 10 minutes.
- API p95 latency > 500ms for 10 minutes.
- PostgreSQL connection utilization > 75% for 10 minutes.
- Queue lag above normal baseline for 15 minutes.

### Critical Alerts (page on-call)
- Error rate > 3% for 5 minutes.
- API p95 latency > 1000ms for 5 minutes.
- Readiness success < 95% for 5 minutes.
- PostgreSQL replication lag > 60s for 5 minutes.
- Any sustained OOM restart loop (>3 restarts/10 minutes).

---

## Rollback Triggers and Procedure

### Automatic/Manual Rollback Triggers
Trigger rollback if any of the following occurs during or immediately after deployment:
- Critical alert threshold breached for >5 minutes.
- Core transaction success rate drops below 98%.
- Canary cohort error rate is >2x baseline.
- Migration causes data integrity or performance regression.
- On-call/service owner cannot mitigate within 15 minutes.

### Rollback Procedure
1. Freeze rollout (stop progressive promotion).
2. Shift traffic back to last known good version.
3. If migration is backward-compatible, keep schema and roll app back.
4. If migration is not backward-compatible, execute DB rollback plan or restore point-in-time backup.
5. Validate service health endpoints and key user journeys.
6. Post incident update with root-cause hypothesis and next action.

---

## PostgreSQL Backup and Restore Procedures

### Backup Policy
- Full logical backup nightly.
- WAL archiving / incremental backup every 5 minutes.
- Retention:
  - dev: 7 days,
  - staging: 14 days,
  - prod: 35 days minimum.
- Backup encryption required at rest and in transit.
- Weekly restore drill in non-production environment.

### Backup Procedure (example)
1. Verify backup destination available and encrypted.
2. Run backup:
   ```bash
   pg_dump -Fc -h <db-host> -U <db-user> -d <db-name> -f <backup-file>.dump
   ```
3. Archive WAL segments (if configured) and upload artifacts.
4. Validate backup integrity:
   ```bash
   pg_restore --list <backup-file>.dump > /dev/null
   ```
5. Record backup metadata (timestamp, size, checksum, operator).

### Restore Procedure (example)
1. Declare incident/change and isolate restore target environment.
2. Provision target PostgreSQL instance with matching major version.
3. Restore backup:
   ```bash
   pg_restore -c -h <db-host> -U <db-user> -d <db-name> <backup-file>.dump
   ```
4. Reapply WAL / point-in-time recovery if required.
5. Run post-restore checks:
   - schema version,
   - row counts on critical tables,
   - integrity constraints,
   - application smoke test.
6. Resume traffic only after owner sign-off.

---

## Secret Rotation Procedure

### Rotation Cadence
- Standard credentials/API keys: every 90 days.
- High-risk credentials (DB admin, cloud root-equivalent): every 30 days.
- Immediate rotation after suspected compromise, team offboarding, or incident.

### Rotation Steps
1. Inventory secret usage (services, jobs, CI, integrations).
2. Create new secret version in secret manager (do not overwrite current immediately).
3. Deploy application configuration referencing new version.
4. Validate authentication/authorization flows and dependent integrations.
5. Revoke old secret version after validation window.
6. Confirm no residual use of old credential via audit logs.
7. Update runbook/change record with rotation timestamp and owner.

### Emergency Rotation
- Trigger incident response.
- Rotate impacted credentials immediately.
- Revoke all potentially exposed keys.
- Force token/session invalidation if applicable.
- Increase monitoring and perform post-incident secret scope reduction.

---

## Operational Checklists

### Pre-Deployment
- [ ] CI green and artifact immutable.
- [ ] Release notes and rollback plan prepared.
- [ ] Backup recency and restore test status verified.
- [ ] On-call and approvers available.

### Post-Deployment
- [ ] Health checks passing.
- [ ] Error/latency/saturation within thresholds.
- [ ] Critical user journeys validated.
- [ ] Deployment communication sent.

### Post-Incident / Rollback
- [ ] Service restored to stable version.
- [ ] Incident timeline documented.
- [ ] Corrective and preventive actions assigned.
