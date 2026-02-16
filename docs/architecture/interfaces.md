# Interface Contracts

This document defines the explicit interface boundaries between task execution agents,
measurement, RLI integrations, and on-chain reputation components.

## 1) Agent interface

Agents are expected to satisfy the `AgentInterface` protocol in
`src/backend/measurement/interfaces.py`.

### Required attributes

- `agent_id: str`
- `experiment_group: str`
- `rep: int`

### Required methods

- `execute_task(task: TaskDefinition) -> Any`
  - Executes the task payload and returns deliverable metadata.
- `request_rli_evaluation(task: TaskDefinition) -> RLIEvaluation`
  - Submission hook used by measurement to request or fetch RLI scoring.
- `update_rep(delta: int) -> int`
  - REP update hook used after measurement finalization.

## 2) Task interface

Tasks must follow `TaskDefinition`:

- `id: str` - globally unique task identifier.
- `category: TaskCategory` - canonical taxonomy (`engineering`, `research`, `operations`, `governance`, `other`).
- `value: float` - economic value used for quality-adjusted value computation.
- `payload: Mapping[str, Any]` - execution payload handed to the agent.
- `acceptance_criteria: Sequence[str]` - machine/human verifiable completion criteria.

## 3) Measurement interface

Measurements persisted by the backend must satisfy the `EfficiencyMeasurementInterface`
contract and include all of the following required fields:

- Identity: `measurement_id`, `agent_id`, `task_id`, `experiment_group`, `timestamp`
- Runtime/cost: `duration_seconds`, `llm_calls`, `compute_cost`, `total_cost`
- RLI result: `rli_automation_rate`, `rli_elo_score`, `rli_comparison_url`
- Outcome: `quality_adjusted_value`, `profit`, `roi`, `efficiency`
- Reputation: `rep_earned`, `post_rep`

## 4) RLI client interface

RLI backends must satisfy `RLIClientInterface` (async contract):

- `create_comparison(ai_deliverable, human_baseline, task_brief) -> str`
- `get_evaluation_result(comparison_id) -> RLIEvaluation`

### Exception taxonomy

- `RetryableRLIClientError`: transient failures (timeouts, 429, upstream 5xx).
- `TerminalRLIClientError`: permanent failures (invalid payload, authorization, unsupported inputs).
- `RLIClientError`: common base class for all client failures.

Callers should only retry errors marked retryable.

## 5) Smart contract interface

Backend-facing wrappers must satisfy `SmartContractInterface` with async methods:

- `request_rli_evaluation(member, task_id, deliverable_ipfs_hash) -> str`
- `get_rli_tasks_completed(member) -> int`
- `get_rli_avg_automation(member) -> int`

Expected Solidity interface for `ForgeREP_RLI`:

### Functions

- `requestRLIEvaluation(address member, uint256 taskId, string deliverableIPFSHash) returns (bytes32 requestId)`
- `fulfillRLIEvaluation(bytes32 requestId, address member, uint256 taskId, uint256 automationRate, uint256 eloScore, uint256 economicValue)`

### Events

- `RLIEvaluationRequested(address indexed member, bytes32 indexed requestId, uint256 taskId)`
- `RLIEvaluationRecorded(address indexed member, uint256 taskId, uint256 automationRate, uint256 eloScore, uint256 repEarned)`

### Errors/reverts expected by backend

- Revert string: `"Budget exhausted"` when `rliEvaluationsUsed >= rliEvaluationBudget`.
