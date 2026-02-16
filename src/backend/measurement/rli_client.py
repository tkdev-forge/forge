"""RLI platform API client interface for PoC."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum


class RLIEvaluationState(str, Enum):
    """Canonical RLI evaluation lifecycle states."""

    PENDING = "pending"
    SUBMITTED = "submitted"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMED_OUT = "timed_out"


TERMINAL_STATES = {
    RLIEvaluationState.COMPLETED,
    RLIEvaluationState.FAILED,
    RLIEvaluationState.TIMED_OUT,
}


@dataclass
class RLIPollingConfig:
    """Polling settings aligned with the integration design document."""

    initial_delay_seconds: float = 2.0
    interval_seconds: float = 2.0
    backoff_multiplier: float = 2.0
    max_interval_seconds: float = 30.0
    max_retries: int = 8
    total_timeout_seconds: float = 120.0
    jitter_seconds: float = 0.25


@dataclass
class RLIComparisonCreateRequest:
    comparison_id: str
    member_address: str
    request_id: str
    task_brief: str
    ai_deliverable: str
    human_baseline: str
    callback_url: str
    callback_hmac_secret_ref: str
    metadata: dict[str, str | int | float | bool | None] = field(default_factory=dict)


@dataclass
class RLIComparisonCreateResponse:
    comparison_id: str
    state: RLIEvaluationState
    submitted_at: datetime
    idempotency_key: str | None = None


@dataclass
class RLIEvaluationResult:
    automation_rate: float
    elo_score: int
    economic_value: float
    comparison_url: str


@dataclass
class RLIEvaluationError:
    code: str
    message: str
    retryable: bool = False


@dataclass
class RLIComparisonStatusResponse:
    comparison_id: str
    state: RLIEvaluationState
    updated_at: datetime | None = None
    result: RLIEvaluationResult | None = None
    error: RLIEvaluationError | None = None


class RLIPlatformClient:
    async def create_comparison(self, request: RLIComparisonCreateRequest) -> RLIComparisonCreateResponse:
        """Create a new RLI comparison and return submitted state metadata."""
        return RLIComparisonCreateResponse(
            comparison_id=request.comparison_id,
            state=RLIEvaluationState.SUBMITTED,
            submitted_at=datetime.utcnow(),
            idempotency_key=f"{request.request_id}:{request.member_address}",
        )

    async def get_evaluation_result(self, comparison_id: str) -> RLIComparisonStatusResponse:
        """Retrieve evaluation status and terminal result (if available)."""
        return RLIComparisonStatusResponse(
            comparison_id=comparison_id,
            state=RLIEvaluationState.COMPLETED,
            updated_at=datetime.utcnow(),
            result=RLIEvaluationResult(
                automation_rate=0.75,
                elo_score=920,
                economic_value=200.0,
                comparison_url=f"https://rli-eval.forge.network/results/{comparison_id}",
            ),
        )


def get_next_poll_delay(attempt: int, config: RLIPollingConfig) -> timedelta:
    """Return exponential-backoff delay for polling attempt (1-indexed)."""

    if attempt <= 1:
        seconds = config.interval_seconds
    else:
        seconds = config.interval_seconds * (config.backoff_multiplier ** (attempt - 1))
    seconds = min(seconds, config.max_interval_seconds)
    return timedelta(seconds=seconds)
