"""Typed interface contracts for measurement and RLI integration boundaries."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Mapping, Protocol, Sequence, runtime_checkable


class TaskCategory(str, Enum):
    """Supported task categories for measurement and RLI evaluation."""

    ENGINEERING = "engineering"
    RESEARCH = "research"
    OPERATIONS = "operations"
    GOVERNANCE = "governance"
    OTHER = "other"


@dataclass(frozen=True)
class TaskDefinition:
    """Canonical task payload exchanged across backend layers."""

    id: str
    category: TaskCategory
    value: float
    payload: Mapping[str, Any]
    acceptance_criteria: Sequence[str]


@dataclass(frozen=True)
class RLIEvaluation:
    """Normalized result returned by RLI services."""

    automation_rate: float
    elo_score: int
    economic_value: float
    comparison_url: str = ""


@runtime_checkable
class AgentInterface(Protocol):
    """Agent boundary used by measurement code."""

    agent_id: str
    experiment_group: str
    rep: int

    def execute_task(self, task: TaskDefinition) -> Any:
        """Execute a task payload and return deliverable metadata."""

    def request_rli_evaluation(self, task: TaskDefinition) -> RLIEvaluation:
        """Invoke RLI evaluation for a completed task."""

    def update_rep(self, delta: int) -> int:
        """Apply REP updates and return the new balance."""


@runtime_checkable
class EfficiencyMeasurementInterface(Protocol):
    """Required fields for measurement records persisted by the tracker."""

    measurement_id: str
    agent_id: str
    task_id: str
    experiment_group: str
    timestamp: datetime
    duration_seconds: float
    llm_calls: int
    compute_cost: float
    rli_automation_rate: float
    rli_elo_score: int
    rli_comparison_url: str
    quality_adjusted_value: float
    total_cost: float
    profit: float
    roi: float
    efficiency: float
    rep_earned: int
    post_rep: int


class RLIClientError(Exception):
    """Base class for RLI client failures."""


class RetryableRLIClientError(RLIClientError):
    """Errors that callers should retry (timeouts, 429, 5xx)."""


class TerminalRLIClientError(RLIClientError):
    """Errors that callers should not retry (validation/auth)."""


@runtime_checkable
class RLIClientInterface(Protocol):
    """Async API contract for RLI evaluation providers."""

    async def create_comparison(self, ai_deliverable: str, human_baseline: str, task_brief: str) -> str:
        """Create a comparison job and return provider comparison ID."""

    async def get_evaluation_result(self, comparison_id: str) -> RLIEvaluation:
        """Resolve a comparison ID into normalized evaluation metrics."""


@dataclass(frozen=True)
class ContractFunctionSignature:
    name: str
    inputs: Sequence[str]
    outputs: Sequence[str]


@dataclass(frozen=True)
class ContractEventSignature:
    name: str
    fields: Sequence[str]


@dataclass(frozen=True)
class ContractErrorSignature:
    name: str
    fields: Sequence[str]


EXPECTED_CONTRACT_FUNCTIONS: Sequence[ContractFunctionSignature] = (
    ContractFunctionSignature(
        name="requestRLIEvaluation",
        inputs=("address member", "uint256 taskId", "string deliverableIPFSHash"),
        outputs=("bytes32 requestId",),
    ),
    ContractFunctionSignature(
        name="fulfillRLIEvaluation",
        inputs=(
            "bytes32 requestId",
            "address member",
            "uint256 taskId",
            "uint256 automationRate",
            "uint256 eloScore",
            "uint256 economicValue",
        ),
        outputs=(),
    ),
)

EXPECTED_CONTRACT_EVENTS: Sequence[ContractEventSignature] = (
    ContractEventSignature(
        name="RLIEvaluationRequested",
        fields=("address indexed member", "bytes32 indexed requestId", "uint256 taskId"),
    ),
    ContractEventSignature(
        name="RLIEvaluationRecorded",
        fields=(
            "address indexed member",
            "uint256 taskId",
            "uint256 automationRate",
            "uint256 eloScore",
            "uint256 repEarned",
        ),
    ),
)

EXPECTED_CONTRACT_ERRORS: Sequence[ContractErrorSignature] = (
    ContractErrorSignature(name="Budget exhausted", fields=()),
)


@runtime_checkable
class SmartContractInterface(Protocol):
    """Backend-facing async wrapper contract for ForgeREP_RLI."""

    async def request_rli_evaluation(self, member: str, task_id: int, deliverable_ipfs_hash: str) -> str:
        """Submit evaluation request and return on-chain request id."""

    async def get_rli_tasks_completed(self, member: str) -> int:
        """Read completed task count from chain."""

    async def get_rli_avg_automation(self, member: str) -> int:
        """Read rolling automation average from chain (scaled integer)."""
