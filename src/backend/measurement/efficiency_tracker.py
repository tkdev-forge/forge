"""Efficiency Tracker for Forge PoC."""

import time
from dataclasses import dataclass
from datetime import datetime


@dataclass
class EfficiencyMeasurement:
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


class EfficiencyTracker:
    def __init__(self, experiment_name: str, db_connection):
        self.experiment_name = experiment_name
        self.db = db_connection

    def track(self, agent, task):
        return MeasurementContext(self, agent, task)


class MeasurementContext:
    def __init__(self, tracker: EfficiencyTracker, agent, task):
        self.tracker = tracker
        self.agent = agent
        self.task = task
        self.start_time = None
        self.llm_call_counter = 0
        self.compute_cost = 0.0

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        rli_result = self._request_rli_evaluation()

        quality_adjusted_value = self.task.economic_value * rli_result.automation_rate
        total_cost = self.compute_cost + 2.34
        profit = quality_adjusted_value - total_cost
        roi = profit / total_cost if total_cost else 0
        rep_earned = self._calculate_rep(rli_result)

        measurement = EfficiencyMeasurement(
            measurement_id=f"{self.agent.agent_id}-{self.task.id}-{int(time.time())}",
            agent_id=self.agent.agent_id,
            task_id=self.task.id,
            experiment_group=self.agent.experiment_group,
            timestamp=datetime.utcnow(),
            duration_seconds=duration,
            llm_calls=self.llm_call_counter,
            compute_cost=self.compute_cost,
            rli_automation_rate=rli_result.automation_rate,
            rli_elo_score=rli_result.elo_score,
            rli_comparison_url=rli_result.comparison_url,
            quality_adjusted_value=quality_adjusted_value,
            total_cost=total_cost,
            profit=profit,
            roi=roi,
            efficiency=quality_adjusted_value / (duration / 3600) if duration else 0,
            rep_earned=rep_earned,
            post_rep=self.agent.rep + rep_earned,
        )
        self._save_measurement(measurement)
        return False

    def _request_rli_evaluation(self):
        return self.agent.request_rli_evaluation(self.task)

    def _calculate_rep(self, rli_result):
        return int((rli_result.automation_rate * rli_result.economic_value) / 100)

    def _save_measurement(self, measurement: EfficiencyMeasurement):
        if hasattr(self.tracker.db, "save_measurement"):
            self.tracker.db.save_measurement(measurement)
