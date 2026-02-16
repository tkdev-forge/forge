"""RLI Chainlink adapter placeholder for PoC."""

from dataclasses import dataclass
from datetime import datetime

from src.backend.measurement.rli_client import RLIEvaluationResult, RLIEvaluationState


@dataclass
class RLIFulfillmentPayload:
    request_id: str
    comparison_id: str
    member_address: str
    state: RLIEvaluationState
    result: RLIEvaluationResult | None = None
    error_code: str | None = None
    error_message: str | None = None
    fulfilled_at: datetime | None = None


@dataclass
class RLIFulfillmentRecord:
    request_id: str
    comparison_id: str
    state: RLIEvaluationState
    result_hash: str
    processed_at: datetime
    is_duplicate: bool = False
    is_conflict: bool = False


class RLIPerformanceOracle:
    async def handle_evaluation_request(self, request_id: str, member_address: str, deliverable_ipfs: str) -> str:
        """Create (or resolve idempotently) a comparison and return its ID."""

        del member_address, deliverable_ipfs
        return f"comparison-{request_id}"

    async def handle_chainlink_fulfillment(self, payload: RLIFulfillmentPayload) -> RLIFulfillmentRecord:
        """Apply idempotent fulfillment semantics for terminal RLI states.

        Implementations must:
        - dedupe by request_id/comparison_id,
        - no-op on exact duplicate payload,
        - preserve first accepted terminal payload on conflict and flag it.
        """

        if payload.state not in {
            RLIEvaluationState.COMPLETED,
            RLIEvaluationState.FAILED,
            RLIEvaluationState.TIMED_OUT,
        }:
            raise ValueError("chainlink fulfillment must be terminal")

        result_hash = f"{payload.request_id}:{payload.comparison_id}:{payload.state}"
        return RLIFulfillmentRecord(
            request_id=payload.request_id,
            comparison_id=payload.comparison_id,
            state=payload.state,
            result_hash=result_hash,
            processed_at=payload.fulfilled_at or datetime.utcnow(),
            is_duplicate=False,
            is_conflict=False,
        )
