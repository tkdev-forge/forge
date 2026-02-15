# Measurement Metrics

## Primary Metric: Automation Rate

**Definition**: % of human-level quality as rated by expert evaluators

**Source**: RLI Platform (3 human evaluators per task)

**Scale**: 0-100%
- 0%: Unusable output
- 50%: Acceptable but needs revision
- 75%: Good quality, minor edits
- 100%: Indistinguishable from human work

**Target**: ≥60% by Month 6

## Secondary Metrics

- Time Efficiency: task duration
- Cost Efficiency: total cost per task
- Quality-Adjusted Productivity (QAP)
- Economic Efficiency
- Learning Rate
- ROI
- Specialization Index

## Measurement Infrastructure

```sql
CREATE TABLE efficiency_measurements (
    measurement_id VARCHAR(128) PRIMARY KEY,
    agent_id VARCHAR(64),
    task_id VARCHAR(64),
    experiment_group VARCHAR(32),
    timestamp TIMESTAMP,
    duration_seconds FLOAT,
    llm_calls INT,
    compute_cost FLOAT,
    rli_automation_rate FLOAT,
    rli_elo_score INT,
    rli_comparison_url TEXT,
    quality_adjusted_value FLOAT,
    total_cost FLOAT,
    roi FLOAT,
    efficiency FLOAT,
    rep_earned INT,
    post_rep INT
);
```
