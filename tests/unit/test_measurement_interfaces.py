from dataclasses import fields
from typing import get_type_hints

import pytest

from src.backend.measurement.efficiency_tracker import EfficiencyMeasurement
from src.backend.measurement.interfaces import (
    EXPECTED_CONTRACT_ERRORS,
    EXPECTED_CONTRACT_EVENTS,
    EXPECTED_CONTRACT_FUNCTIONS,
    EfficiencyMeasurementInterface,
    RLIClientError,
    RLIClientInterface,
    RetryableRLIClientError,
    TaskCategory,
    TaskDefinition,
    TerminalRLIClientError,
)
from src.backend.measurement.rli_client import RLIPlatformClient


REQUIRED_MEASUREMENT_FIELDS = {
    "measurement_id",
    "agent_id",
    "task_id",
    "experiment_group",
    "timestamp",
    "duration_seconds",
    "llm_calls",
    "compute_cost",
    "rli_automation_rate",
    "rli_elo_score",
    "rli_comparison_url",
    "quality_adjusted_value",
    "total_cost",
    "profit",
    "roi",
    "efficiency",
    "rep_earned",
    "post_rep",
}


def test_task_definition_shape():
    task = TaskDefinition(
        id="task-123",
        category=TaskCategory.ENGINEERING,
        value=125.0,
        payload={"ticket": "FORGE-1"},
        acceptance_criteria=("all tests pass",),
    )

    assert task.id == "task-123"
    assert task.category is TaskCategory.ENGINEERING
    assert task.value == pytest.approx(125.0)
    assert task.payload["ticket"] == "FORGE-1"
    assert task.acceptance_criteria[0] == "all tests pass"


def test_efficiency_measurement_has_required_contract_fields():
    measurement_fields = {item.name for item in fields(EfficiencyMeasurement)}
    assert REQUIRED_MEASUREMENT_FIELDS.issubset(measurement_fields)


def test_efficiency_measurement_is_runtime_protocol_compatible():
    annotations = get_type_hints(EfficiencyMeasurement)
    protocol_annotations = get_type_hints(EfficiencyMeasurementInterface)
    for field_name in REQUIRED_MEASUREMENT_FIELDS:
        assert field_name in annotations
        assert annotations[field_name] == protocol_annotations[field_name]


def test_rli_platform_client_implements_protocol():
    client = RLIPlatformClient()
    assert isinstance(client, RLIClientInterface)


def test_rli_error_hierarchy():
    retryable = RetryableRLIClientError("retry")
    terminal = TerminalRLIClientError("terminal")

    assert isinstance(retryable, RLIClientError)
    assert isinstance(terminal, RLIClientError)
    assert not isinstance(retryable, TerminalRLIClientError)


def test_expected_contract_surface_is_declared():
    function_names = {item.name for item in EXPECTED_CONTRACT_FUNCTIONS}
    event_names = {item.name for item in EXPECTED_CONTRACT_EVENTS}
    error_names = {item.name for item in EXPECTED_CONTRACT_ERRORS}

    assert "requestRLIEvaluation" in function_names
    assert "fulfillRLIEvaluation" in function_names
    assert "RLIEvaluationRequested" in event_names
    assert "RLIEvaluationRecorded" in event_names
    assert "Budget exhausted" in error_names
