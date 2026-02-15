# Research Hypotheses

⚠️ **IMPORTANT**: These are **untested hypotheses**. 
No experiment has been run yet. All projections below are theoretical.

---

## Primary Hypothesis (H1)

**Statement**: AI agents embedded in economic systems with real incentives (REP decay + task rewards) will reach ≥60% human-level automation rate within 6 months

**Rationale**:
- Traditional benchmarks use static task pools → agents memorize
- Forge uses dynamic task assignment → agents must generalize
- REP decay creates continuous improvement pressure
- M2M economy creates competitive selection pressure
- RLI paper shows 87.5% performance gap that economic incentives may close

**Measurement**: RLI Automation Rate (0-100%)

**Success Criterion**: ≥60% by Month 6

**Projected Outcome** (if hypothesis correct): 
- Month 0: ~25% (baseline)
- Month 3: ~58% (on track)
- Month 6: ~72% (exceeds target)

**Actual Status**: 
- [ ] Experiment deployed
- [ ] Data collection started
- [ ] Hypothesis tested
- [ ] Results validated

**Expected Testing Timeline**: April - September 2026

**Falsification Criterion**: If automation rate <50% by Month 6, hypothesis is REJECTED

---

## Secondary Hypotheses

### H2: Learning Rate

**Statement**: Forge agents improve 3x faster than isolated agents due to economic feedback loops

**Measurement**: Δ Automation Rate per 100 tasks

**Projected Outcomes**:
- **Control Group** (isolated agents): +1.5% per 100 tasks
- **Treatment Group** (Forge): +4.5% per 100 tasks (3x faster)

**Rationale**: 
- REP decay forces continuous improvement
- M2M markets reward better performers
- Task selection driven by proven competence
- Specialization through repeated practice

**Actual Status**: ⏳ Awaiting pilot deployment

**Falsification Criterion**: If Forge improvement ≤1.5x control group, hypothesis REJECTED

---

### H3: Specialization

**Statement**: Economic incentives drive agents to specialize (focus on specific task categories) rather than generalize

**Measurement**: Gini coefficient of task category distribution
- 0.0 = Perfect generalist (equal distribution across all 23 categories)
- 1.0 = Perfect specialist (only one category)

**Projected**: Gini >0.5 (specialists)

**Rationale**:
- REP rewards excellence, not breadth
- Specialization reduces failure rate
- M2M markets develop niches
- Similar to human freelancer behavior

**Actual Status**: ⏳ Awaiting pilot deployment

**Falsification Criterion**: If Gini <0.3, agents are generalists and hypothesis REJECTED

---

### H4: Multi-Agent Synergy

**Statement**: Teams of specialized agents outperform solo generalist agents on complex tasks (>$500 value)

**Measurement**: Team automation rate vs. Solo automation rate on high-value tasks

**Projected**: Team ≥ 1.15 × Solo (15% improvement)

**Rationale**:
- Complex tasks require multiple skills
- Specialists have deeper expertise
- Coordination overhead <15%
- Forge's M2M economy facilitates collaboration

**Actual Status**: ⏳ Planned for Month 6+ (after agents specialize)

**Falsification Criterion**: If Team ≤1.05 × Solo, no synergy exists and hypothesis REJECTED

---

## Statistical Power Analysis

**Pre-registered Design**:
- **Sample Size**: 25 agents per group (control vs treatment)
- **Statistical Power**: 80% to detect 20% difference in automation rate
- **Significance Level**: α = 0.05
- **Effect Size**: Cohen's d = 0.8 (large effect expected)
- **Test**: Two-sample t-test for primary comparison

**Rationale for Effect Size**:
Based on RLI paper's observed 87.5% gap between benchmark (SWE-bench 90%) and real-world (2.5%), we expect economic incentives to close 30-50% of this gap, yielding large measurable effects.

**Minimum Detectable Effect**: 15% difference in automation rate

---

## Testing Timeline

| Milestone | Date | Status | Deliverable |
|-----------|------|--------|-------------|
| Hypothesis Formulation | Feb 2026 | ✅ Complete | This document |
| Pre-registration | Mar 2026 | 🚧 In Progress | OSF registration |
| Implementation Complete | Mar 2026 | 🚧 20% Done | Working PoC |
| Pilot Start | Apr 2026 | ⏳ Planned | 10 agents deployed |
| First Data | May 2026 | ⏳ Planned | 100 task completions |
| H1 Test (Month 3) | Jun 2026 | ⏳ Planned | Interim analysis |
| H1 Test (Month 6) | Sep 2026 | ⏳ Planned | Primary endpoint |
| H3 Test (Specialization) | Sep 2026 | ⏳ Planned | Gini analysis |
| H4 Test (Multi-Agent) | Oct 2026 | ⏳ Planned | Team experiments |
| Full Study Complete | Jun 2027 | ⏳ Planned | Final results |
| Paper Submission | Jul 2027 | ⏳ Planned | Conference paper |

---

## Falsification Criteria

**We will REJECT our hypotheses if**:

1. **H1 Rejected** if:
   - Automation rate <50% by Month 6
   - No statistically significant improvement over baseline
   - Control group performs equally well (no effect of economic system)

2. **H2 Rejected** if:
   - Forge learning rate ≤1.5x control group
   - Both groups plateau at same rate
   - Learning curves converge

3. **H3 Rejected** if:
   - Gini coefficient <0.3 (generalists)
   - No significant difference in task distribution vs random
   - Specialization does not correlate with performance

4. **H4 Rejected** if:
   - Team performance ≤1.05x solo performance
   - Coordination overhead >15%
   - No synergy on complex tasks

**Overall Study Success**:
- **Strong Confirmation**: All 4 hypotheses confirmed
- **Partial Confirmation**: 2-3 hypotheses confirmed
- **Weak/No Confirmation**: 0-1 hypotheses confirmed

---

## Pre-Registration Commitment

**Before any data collection begins**, we will:

1. **Register hypotheses** on OSF (Open Science Framework)
2. **Lock analysis plan** (cannot be changed post-hoc)
3. **Specify stopping rules** (when to end experiment)
4. **Define success criteria** (numerical thresholds)
5. **Commit to publishing** all results (positive or negative)

**Registration URL**: [Will be added when complete]

---

## Theoretical Foundation

### Economic Theory:
- **Principal-Agent Theory**: Incentives align behavior with goals
- **Tournament Theory**: Competition improves performance
- **Specialization Theory**: Division of labor increases efficiency

### AI Research:
- **RLI Paper**: Shows 87.5% benchmark-reality gap
- **Reinforcement Learning**: Reward signals drive learning
- **Multi-Agent Systems**: Cooperation emerges in markets

### Key Assumption:
If AI agents respond to economic incentives similarly to humans, then economic system design matters as much as model architecture.

---

## Risk of Null Results

**What if all hypotheses are rejected?**

That would be a **valuable negative result** showing:
1. Current agents don't respond to economic incentives
2. Benchmark performance doesn't transfer to real tasks
3. Economic system design is insufficient

**Alternative explanations if hypotheses fail**:
- Agents lack necessary reasoning capabilities
- RLI tasks too complex for current models
- 6 months too short for learning
- Economic incentives incorrectly designed
- REP decay rate wrong (too fast/slow)

**We commit to publishing** regardless of outcome.

---

## Data Availability

**Current Data**: NONE (❌ experiment not started)

**Future Data** (when experiment runs):
- All agent execution logs
- All RLI evaluation results
- All REP transactions
- All learning curves
- All statistical analyses

**Data Release Plan**: 
- Raw data on GitHub (CC BY 4.0)
- Processed data in paper appendix
- Interactive dashboard for exploration
- Reproducibility package (code + data)

---

**Last Updated**: February 15, 2026  
**Status**: Pre-deployment (no data collected yet)  
**Next Update**: After pre-registration complete (March 2026)
