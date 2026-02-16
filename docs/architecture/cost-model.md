# Forge Pilot Cost Model

## Purpose
This document defines the operating cost equations, budget guardrails, and reporting requirements for pilot runs that use RLI-backed evaluations and on-chain execution.

## Cost Variables

### Indexing
- `N_tasks_day`: number of evaluated tasks per day.
- `N_tasks_week`: number of evaluated tasks per week.
- `N_fail`: number of failed or retried operations.
- `N_runs`: number of pilot run executions.

### Unit Cost Inputs
- `C_rli_eval`: cost per RLI evaluation (USD).
- `G_used`: gas units consumed per on-chain operation.
- `P_gas`: gas price in gwei.
- `P_native_usd`: native chain token price in USD.
- `C_compute_hour`: compute price per runtime hour (USD/hour).
- `H_compute`: runtime hours consumed.
- `C_storage_gb_month`: storage price in USD per GB-month.
- `GB_stored`: average persisted data volume in GB.
- `D_days`: number of elapsed days in run window.

## Per-Operation Cost Equations

### 1) RLI Cost
Per operation:

`Cost_rli_op = C_rli_eval`

Daily:

`Cost_rli_day = N_tasks_day * C_rli_eval`

### 2) On-Chain Gas Cost
Per operation gas cost (USD):

`Cost_gas_op = G_used * P_gas * 1e-9 * P_native_usd`

Where `1e-9` converts gwei to native token.

Daily:

`Cost_gas_day = N_tasks_day * Cost_gas_op`

### 3) Compute Cost
Per operation (if average runtime per task is `H_task`):

`Cost_compute_op = H_task * C_compute_hour`

Daily aggregate (runtime-derived):

`Cost_compute_day = H_compute * C_compute_hour`

### 4) Storage Cost
Daily storage burn from GB-month pricing:

`Cost_storage_day = (GB_stored * C_storage_gb_month) / 30`

Per operation allocation:

`Cost_storage_op = Cost_storage_day / max(N_tasks_day, 1)`

### 5) Total Unit and Aggregate Cost
Per operation all-in burn:

`Cost_total_op = Cost_rli_op + Cost_gas_op + Cost_compute_op + Cost_storage_op`

Daily all-in burn:

`Cost_total_day = Cost_rli_day + Cost_gas_day + Cost_compute_day + Cost_storage_day`

Weekly all-in burn:

`Cost_total_week = sum(Cost_total_day over 7 days)`

## Budget Thresholds for Pilot Runs

### Baseline Budget Bands
Set these at pilot kickoff and store in configuration (`config/pilot-budgets.yaml` when created):

- `B_day_soft`: daily soft budget warning threshold.
- `B_day_hard`: daily hard-stop threshold.
- `B_week_soft`: weekly soft budget warning threshold.
- `B_week_hard`: weekly hard-stop threshold.
- `B_run_cap`: max total budget for a full pilot run.
- `B_unit_cap`: maximum acceptable `Cost_total_op`.

Recommended initial envelope:
- Soft thresholds at 80% of approved budget.
- Hard thresholds at 100% of approved budget.
- Emergency threshold at 110% of approved budget for forced termination logic.

## Automated Stop Conditions
A pilot run must automatically pause or stop when any condition below is met.

### Warning (soft) conditions
Trigger alert + required operator acknowledgement:

1. `Cost_total_day >= B_day_soft`
2. Rolling 7-day cost `>= B_week_soft`
3. `Cost_total_op >= 0.9 * B_unit_cap`

### Hard stop conditions
Trigger immediate halt of new task intake and contract submissions:

1. `Cost_total_day >= B_day_hard`
2. Rolling 7-day cost `>= B_week_hard`
3. Cumulative run cost `>= B_run_cap`
4. `Cost_total_op >= B_unit_cap` for `K` consecutive tasks (default `K=5`)
5. Failure-amplified burn: `(N_fail / max(N_tasks_day,1)) > 0.2` and `Cost_total_day >= B_day_soft`

### Emergency stop conditions
Trigger full run termination and incident process:

1. `Cost_total_day >= 1.1 * B_day_hard`
2. Any single task with `Cost_total_op >= 1.25 * B_unit_cap`
3. Repeated hard-stop events on 3 consecutive days

## Burn Reporting Metrics

### Canonical Metric Names
Use consistent names across logging, monitoring, and dashboard queries.

### Cost metrics (USD)
- `forge.cost.rli.op_usd`
- `forge.cost.gas.op_usd`
- `forge.cost.compute.op_usd`
- `forge.cost.storage.op_usd`
- `forge.cost.total.op_usd`
- `forge.cost.rli.day_usd`
- `forge.cost.gas.day_usd`
- `forge.cost.compute.day_usd`
- `forge.cost.storage.day_usd`
- `forge.cost.total.day_usd`
- `forge.cost.total.week_usd`
- `forge.cost.total.run_usd`

### Volume and efficiency metrics
- `forge.tasks.evaluated.count`
- `forge.tasks.failed.count`
- `forge.tasks.retry_rate`
- `forge.cost.usd_per_successful_task`
- `forge.cost.usd_per_accepted_task`

### Budget and guardrail metrics
- `forge.budget.day.soft_usd`
- `forge.budget.day.hard_usd`
- `forge.budget.week.soft_usd`
- `forge.budget.week.hard_usd`
- `forge.budget.run.cap_usd`
- `forge.budget.unit.cap_usd`
- `forge.stop_condition.warning.count`
- `forge.stop_condition.hard_stop.count`
- `forge.stop_condition.emergency_stop.count`

## Dashboard Requirements

### Daily burn dashboard (required views)
1. **Daily total burn**
   - Line chart: `forge.cost.total.day_usd` (last 30 days).
   - Overlay: `forge.budget.day.soft_usd`, `forge.budget.day.hard_usd`.
2. **Cost composition**
   - Stacked bar: RLI vs gas vs compute vs storage daily components.
3. **Unit economics**
   - Trend for `forge.cost.total.op_usd` and `forge.cost.usd_per_successful_task`.
4. **Guardrail status**
   - Current state card: NORMAL / WARNING / HARD STOP / EMERGENCY STOP.
   - Count cards for stop-condition events in last 24h.

### Weekly burn dashboard (required views)
1. **Weekly aggregate burn**
   - Line/bar chart: `forge.cost.total.week_usd` with weekly thresholds.
2. **Budget utilization**
   - Gauge: `forge.cost.total.run_usd / forge.budget.run.cap_usd`.
3. **Runway estimate**
   - Projection: remaining budget / 7-day moving average burn.
4. **Efficiency by cohort**
   - Compare cost per successful task by task type, model, and environment.

### Alerting requirements
- Warning alerts at soft threshold crossings (Slack + email).
- Paging alerts at hard-stop and emergency-stop crossings.
- Alerts include:
  - current value,
  - threshold breached,
  - trailing 7-day burn,
  - top contributing component (RLI/gas/compute/storage).

## Implementation Notes
- Compute all cost components at task finalization and emit metric events atomically.
- Recompute daily and weekly rollups from source-of-truth events once per hour.
- Stop-condition evaluation should run on every finalized task and on hourly rollups.
