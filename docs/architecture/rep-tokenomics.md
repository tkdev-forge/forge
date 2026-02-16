# REP Tokenomics Specification (RLI-Integrated)

> **Source of truth:** All `ForgeREP` and `ForgeREP_RLI` smart-contract implementations, across all repositories, **MUST** conform to this specification.

## 1) Mint / Reward Formula

### Inputs and units

- `automation_rate` (`uint256`): task automation performance, scaled to `AUTOMATION_RATE_SCALE = 100000`.
  - `100000` = 100.000% automation.
  - `50000` = 50.000% automation.
- `elo_score` (`uint256`): RLI evaluator score.
  - Baseline is `ELO_BASELINE = 1000`.
  - Bonus applies only above baseline.
- `economic_value` (`uint256`): integer-valued on-chain task value used for REP calculation.

### Formula

Constants:

- `AUTOMATION_RATE_SCALE = 100000`
- `ELO_BASELINE = 1000`
- `ELO_BONUS_DIVISOR = 10`
- `MAX_REP_REWARD = 1_000_000`

Computation order:

1. `base_rep = floor(min(automation_rate, AUTOMATION_RATE_SCALE) * economic_value / AUTOMATION_RATE_SCALE)`
2. `normalized_elo = has_elo_score ? elo_score : ELO_BASELINE`
3. `elo_bonus = normalized_elo > ELO_BASELINE ? floor((normalized_elo - ELO_BASELINE) / ELO_BONUS_DIVISOR) : 0`
4. `raw_reward = base_rep + elo_bonus`
5. `rep_reward = min(raw_reward, MAX_REP_REWARD)`

If `economic_value == 0`, reward is forced to `0` (no base reward and no ELO-only reward).

### On-chain rounding behavior

All divisions use Solidity integer division (`uint256`), so rounding is always **toward zero**.

## 2) Decay Formula

Decay applies in `ForgeREP.updateREP` and is **linear by elapsed months**, not exponential compounding.

Constants:

- `DECAYRATE = 5` (5% per month)
- `MONTH = 30 days`
- `DECAY_CAP_PERCENT = 50`

Given `old_rep` and `months_elapsed = floor((block.timestamp - lastUpdate) / MONTH)`:

1. `raw_decay = floor(old_rep * DECAYRATE * months_elapsed / 100)`
2. `max_decay = floor(old_rep * DECAY_CAP_PERCENT / 100)`
3. `decay = min(raw_decay, max_decay)`
4. `rep_after_decay = max(old_rep - decay, 0)`

The cap enforces a maximum 50% reduction in one update call, even after long inactivity.

## 3) Edge-case Rules

- **Missing RLI/ELO score:** If oracle payload marks ELO as missing (`has_elo_score = false`), use baseline `1000` so ELO bonus is `0`.
- **Zero/negative-value tasks:**
  - `economic_value == 0` yields `0` REP.
  - Negative economic values are invalid off-chain and cannot be represented on-chain (`uint256`). Oracle adapters must reject them before fulfillment.
- **Oracle timeout:** Pending requests expire after `ORACLE_TIMEOUT = 1 days`; admin may cancel expired requests and refund one evaluation budget unit.
- **Capped rewards:** Final reward is clamped to `MAX_REP_REWARD`.

## 4) Worked Examples (exact integer math)

### Example A: Normal reward with truncation

Inputs:

- `automation_rate = 33333`
- `has_elo_score = true`
- `elo_score = 1137`
- `economic_value = 999`

Math:

- `base_rep = floor(33333 * 999 / 100000) = floor(33,299,667 / 100000) = 332`
- `elo_bonus = floor((1137 - 1000) / 10) = floor(137 / 10) = 13`
- `raw_reward = 332 + 13 = 345`
- `rep_reward = min(345, 1_000_000) = 345`

### Example B: Missing ELO score

Inputs:

- `automation_rate = 50000`
- `has_elo_score = false`
- `elo_score = 0` (ignored)
- `economic_value = 1000`

Math:

- `base_rep = floor(50000 * 1000 / 100000) = 500`
- `normalized_elo = 1000`
- `elo_bonus = 0`
- `rep_reward = 500`

### Example C: Zero economic value

Inputs:

- `automation_rate = 100000`
- `has_elo_score = true`
- `elo_score = 1800`
- `economic_value = 0`

Math:

- `rep_reward = 0` (forced by zero-value rule)

### Example D: Reward cap

Inputs:

- `automation_rate = 100000`
- `has_elo_score = true`
- `elo_score = 5000`
- `economic_value = 2_500_000`

Math:

- `base_rep = floor(100000 * 2,500,000 / 100000) = 2,500,000`
- `elo_bonus = floor((5000 - 1000) / 10) = 400`
- `raw_reward = 2,500,400`
- `rep_reward = min(2,500,400, 1,000,000) = 1,000,000`

### Example E: Decay schedule and cap (linear)

Inputs:

- `old_rep = 1000`
- `months_elapsed = 11`

Math:

- `raw_decay = floor(1000 * 5 * 11 / 100) = 550`
- `max_decay = floor(1000 * 50 / 100) = 500`
- `decay = min(550, 500) = 500`
- `rep_after_decay = 1000 - 500 = 500`

Result: decay is capped at 50%, not compounded month-over-month.
