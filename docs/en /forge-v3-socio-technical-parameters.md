Erstelle in GitHub **`docs/en/forge-v3-socio-technical-parameters.md`** und füge diesen Text ein:

```markdown
# Forge V3: Socio-Technical Parameters & Domain Profiles

*Supplement to the Forge V3 Architecture Documentation*  
**Version 1.0 | February 2026**

---

## Executive Summary

Forge V3 defines reputation (REP), governance thresholds, and M2M transaction limits through technical parameters such as decay-rate, activity-booster, and REP thresholds. These parameters are not just technical variables – they encode implicit social expectations about work rhythms, contribution forms, and power dynamics.

This document shows:

1. **Why parameters have social meaning:** Decay-rate and booster formulas effectively define the “work speed” the system expects.  
2. **Domain-specific profiles:** Research DAOs, FMCG product economies, and city DAOs need fundamentally different parameter settings.  
3. **Tuning via simulation:** Parameters can and should be simulated and “played with” before deployment.  
4. **Design-space constraints:** The policy-layer should prevent extreme parameters without disempowering communities.

Target audience: Forge deployers, DAO founders, governance designers who want to understand how technical parameters shape social realities. [file:2]

---

## 1. Technical Parameters as Social Design Decisions

### 1.1 What the Red Queen Formula Really Means

The Red Queen formula in the Forge V3 reputation-layer is:

\[
REP_{new} = REP_{old} \times (1 - Decay\_Rate) + \alpha \times \frac{Activity}{Community\_Avg}
\]

At first glance: a mathematical formula for dynamic reputation.  
At second glance: an implicit statement about how often and in what form people must contribute in order to retain power.

### 1.2 Parameters as “Expectation Encoders”

| Parameter | Technical Definition | Social Meaning |
|----------|----------------------|----------------|
| **Decay-Rate** | % REP loss per month when inactive | “How quickly do you lose influence when you pause?” |
| **Activity-Booster (α)** | Multiplier for activity relative to community-average | “How strongly does the system reward above-average contributions?” |
| **Community-Avg-Window** | Time window for calculating the average (e.g. 30 days) | “Over what period is comparability defined?” |
| **REP-Thresholds** | Minimum REP for access/proposal/veto | “Who is allowed to speak and decide at all?” |

### 1.3 The Hidden “Work Speed”

Example: **Decay-Rate = 5% per month**

- After 6 months without contributions: \(REP \times 0.95^6 \approx 0.735 \times REP\) (≈ 26.5% loss)  
- After 12 months: \(REP \times 0.95^{12} \approx 0.540 \times REP\) (≈ 46% loss)

**Social consequence:**

Anyone who works on a project for more than 3–4 months without visible intermediate outputs (commits, skills, votes) loses significant REP—even if the work is high-quality.

The system implicitly “expects”:

- Visible contributions every 1–2 months, otherwise power loss.  

For a **research DAO** where papers take 6–18 months, this is toxic.  
For an **FMCG product company** with weekly sprints, it is appropriate.

---

## 2. Domain-Specific Parameter Profiles

### 2.1 Why “One Size Fits All” Does Not Work

Different organization types have fundamentally different:

- **Contribution rhythms:** From daily commits to multi-year research projects.  
- **Quality signals:** Code commits vs peer review vs customer feedback vs energy efficiency.  
- **Power dynamics:** Fast iteration vs long-term stability.

Forge V3 is **domain-agnostic** – but parameters must be configured **domain-specific**.

### 2.2 Example Profiles

#### Profile A: Research DAO

**Characteristics:**

- Long project cycles (6–24 months)  
- Quality > quantity  
- Peer review and reproducibility are key  
- Risk: “Publish or perish” pressure vs deep, slow work

**Recommended parameters:**

| Parameter | Value | Rationale |
|----------|-------|-----------|
| **Decay-Rate** | 2% per month | Allows 12–18 months of deep work without critical REP loss |
| **Activity-Booster (α)** | 50 (lower) | Less focus on “above-average”, more on absolute quality |
| **Community-Avg-Window** | 90 days | Longer comparison window, smooths fluctuations |
| **Proposal-Threshold** | 100 REP or 15% above avg | Higher hurdle, more stable governance |
| **Quality-Oracles** | Citations, replications, peer review | Not just commit frequency |

**Result:**  
System tolerates pauses and rewards impact rather than output frequency.

#### Profile B: FMCG Product Economy

**Characteristics:**

- Short release cycles (weeks, days)  
- Fast iteration, A/B-testing  
- Market and customer feedback as quality signals  
- Risk: technical debt due to rush

**Recommended parameters:**

| Parameter | Value | Rationale |
|----------|-------|-----------|
| **Decay-Rate** | 6% per month | Forces continuous activity, fast power rotation |
| **Activity-Booster (α)** | 150 (higher) | Strong reward for above-average output |
| **Community-Avg-Window** | 14 days | Short window, reacts quickly |
| **Proposal-Threshold** | 50 REP or 10% above avg | Lower hurdle, faster decisions |
| **Quality-Oracles** | Bug-rate, customer satisfaction, test coverage | Quality as counterweight to speed |

**Result:**  
System enforces tempo but prevents “quick & dirty” via quality-gates.

#### Profile C: City DAO

**Characteristics:**

- Very diverse contribution types (citizen participation, infrastructure, events, data)  
- Long-term stability important  
- Broad participation > elite dominance  
- Risk: apathy vs populism

**Recommended parameters:**

| Parameter | Value | Rationale |
|----------|-------|-----------|
| **Decay-Rate** | 3% per month | Moderate erosion, tolerates normal citizen rhythms |
| **Activity-Booster (α)** | 80 (moderate) | Rewards engagement but not extremely |
| **Community-Avg-Window** | 60 days | Medium horizon, buffers seasonal fluctuations |
| **Proposal-Threshold** | Absolute: 30 REP (not relative) | Accessible for normal citizens |
| **Quality-Oracles** | Peer endorsements, event participation, node hosting | Diverse contribution forms |

**Result:**  
Broad participation possible, slow governance, stable power structures.

---

## 3. Simulation and “Gaming” for Parameter Discovery

### 3.1 The Problem of Blind Parameter Choice

Without simulation, effects of parameter-combinations are not intuitive:

- How does REP distribution change after 12 months?  
- Which activity patterns “survive”?  
- When do systems tip into stagnation or frenzy?

**Solution:** Simulate before deployment.

### 3.2 Agent-Based Simulation (Off-Chain)

**Approach:**

1. Define synthetic persona-populations:
   - Slow thinkers: 1 large contribution every 6 months  
   - Steady workers: 10 small contributions per month  
   - Burst contributors: 100 contributions in month 1, then 6 months pause  
   - Inactives: No contributions after month 3  

2. Simulate 24 months with different parameter-sets:
   - Decay ∈ {2%, 5%, 8%}  
   - Booster α ∈ {50, 100, 150}  

3. Measure outcomes:
   - REP distribution (Gini coefficient)  
   - Governance participation (% active voters)  
   - “Survivor bias”: which persona-types dominate?

**Example result:**

- With Decay = 8% + α = 150, only **steady workers** and **burst contributors** survive.  
- “Slow thinkers” lose 60% REP after 12 months → system discriminates deep work.

### 3.3 “Gaming” with Real Humans

**Approach:**

- Build a sandbox instance of Forge with play-money (test REP, testnet tokens).

**Game rules:**

- 50–100 participants receive initial REP.  
- They can complete tasks (simulated commits, votes, skill-publishes).  
- Parameters are varied (Group A: Decay=2%, Group B: Decay=6%).  

After 3 months: survey + data-analysis.

**Outcome:**

- Qualitative insights: “With 6% decay it feels rushed.”  
- Quantitative data: REP distribution, churn rate.

### 3.4 Tuning Oracles for Live Systems

Forge can collect meta-metrics and derive parameter suggestions:

| Metric | Meaning | Example Suggestion |
|--------|---------|--------------------|
| **Median contribution interval** | How often do people typically contribute? | “Median = 40 days but decay expects 20 → lower decay from 5% to 3%.” |
| **REP concentration (Gini)** | How unequal is power? | “Top 10% hold 80% REP → increase booster for new members.” |
| **Governance participation** | % of REP holders that vote | “Only 15% vote → lower proposal-threshold from 100 to 50 REP.” |
| **Churn rate** | % members inactive after 6 months | “40% churn → decay too high or onboarding issue?” |

**Flow:**

1. Oracle gathers on-chain + off-chain data.  
2. ML-model generates parameter-adjustment proposal.  
3. Proposal enters governance system → community votes.  
4. If approved: smart contract updates parameters.

---

## 4. Policy-Layer Design-Space Constraints

### 4.1 Why Unbounded Parameters Are Dangerous

Without bounds, a DAO could:

- Set Decay = 50% per month → system collapses into frenzy.  
- Set Decay = 0% → old elites freeze, no rotation.  
- Set Proposal-Threshold = 10,000 REP → only founders can propose, community disempowered.

Problem: Communities without experience might choose toxic parameters.

### 4.2 Solution: Allowed Intervals in Policy-Contract

The policy-layer should define **min/max bounds** for critical parameters:

```solidity
contract ForgePolicy {
    uint256 public constant MIN_DECAY = 1;  // 1% per month
    uint256 public constant MAX_DECAY = 10; // 10% per month
    uint256 public constant MIN_BOOSTER = 50;
    uint256 public constant MAX_BOOSTER = 200;

    function updateDecayRate(uint256 newRate) external onlyDAO {
        require(newRate >= MIN_DECAY && newRate <= MAX_DECAY, "Decay out of allowed range");
        decayRate = newRate;
    }
}
```

**Effect:**

- Extreme settings are technically prevented.  
- DAO keeps flexibility within reasonable bounds.  
- Bounds themselves can be changed via super-majority vote (e.g. 80%).

### 4.3 Domain Profiles as Smart Contract Presets

During Genesis-bootstrap the DAO can choose a profile:

```python
# Genesis script
profile = input("Choose profile: [research / product / city]")

if profile == "research":
    decay_rate = 2
    booster = 50
    window = 90
elif profile == "product":
    decay_rate = 6
    booster = 150
    window = 14
elif profile == "city":
    decay_rate = 3
    booster = 80
    window = 60

deploy_contracts(decay_rate, booster, window)
```

**Advantage:**

- Founders do not have to invent parameters “from scratch”.  
- They start with proven presets and can iterate.

---

## 5. Implementation Roadmap

### 5.1 Phase 1: Documentation & Presets (Month 1–2)

**Deliverables:**

- Three reference-profiles documented (Research, Product, City)  
- Parameter ranges defined in policy-contract  
- Genesis-script extended with profile-selection

### 5.2 Phase 2: Simulation Framework (Month 3–6)

**Deliverables:**

- Agent-based simulation in Python (Mesa framework)  
- Web-UI for parameter tests  
- Sample data for 5 different parameter-sets

### 5.3 Phase 3: Gaming Sandbox (Month 7–9)

**Deliverables:**

- Testnet instance of Forge with game mechanics  
- 100 beta-testers for 3‑month experiment  
- Evaluation report: qualitative + quantitative feedback

### 5.4 Phase 4: Tuning Oracles (Month 10–12)

**Deliverables:**

- Meta-metric collection in monitoring-layer  
- ML-model for parameter suggestions  
- Integration into proposal-system

---

## 6. Best Practices for DAO Founders

### 6.1 Checklist: Parameter Choice at Genesis-Bootstrap

- Identify domain: research? product? city? other?  
- Choose reference-profile: start from proven preset.  
- Adjust: if needed, modify slightly (±20% from preset).  
- Simulate: use simulation-tool to see 12‑month projection.  
- Document: explain to community why these parameters were chosen.  
- Set review-point: “After 6 months we evaluate parameters via proposal.”

### 6.2 Warning Signs for Toxic Parameters

| Symptom | Possible Cause | Intervention |
|---------|----------------|-------------|
| High churn (>40% after 6 months) | Decay too high, system too stressful | Lower decay by 1–2% |
| REP-freeze (top 10% hold >80% over 12 months) | Decay too low, no rotation | Increase decay, strengthen booster |
| Governance apathy (<20% voting participation) | Thresholds too high, community feels powerless | Lower proposal/veto thresholds |
| Hectic output, poor quality | Decay + booster too high, quantity over quality | Lower booster, add quality-oracles |

### 6.3 Iterative Tuning as Culture

**Principle:**  
Parameters are not sacred constants but **hypotheses** about social dynamics.

**Recommendation:**

- Every 6 months: “Parameter review proposal” via governance.  
- Use monitoring-data (REP distribution, churn, voting rate).  
- A/B-test in sandboxes before mainnet changes.

---

## 7. Limits and Open Questions

### 7.1 What Simulation Cannot Solve

- **Strategic gaming:** People will find ways to game oracles and formulas (e.g. many small meaningless commits).  
- **Quality assessment:** What is “good research”? What is “good code”? Oracles can measure proxies, not truth.  
- **Cultural factors:** Burnout, toxicity, trust are not purely parametrically controllable.

### 7.2 Open Research Questions

1. Optimal decay-curves: linear? exponential? piecewise (different by REP-level)?  
2. Multi-dimensional REP: should there be REP-types (code-REP, governance-REP, review-REP)?  
3. Time-dependent booster: should booster decrease over DAO lifetime (early phase high, late phase lower)?  
4. Cross-domain transfer: can REP from ResearchDAO be ported into ProductDAO (with discount)?

---

## 8. Summary & Recommendations

**Key message:**  
Technical parameters in Forge V3 are never “just technical”—they encode implicit social norms about work rhythms, power distribution, and notions of quality.

**As a Forge deployer you should:**

1. **Choose consciously:** Use domain-profiles instead of blindly taking defaults.  
2. **Simulate before deployment:** Test parameters in agent simulations and/or gaming sandboxes.  
3. **Constrain design-space:** Define min/max bounds in policy-layer.  
4. **Iterate:** Treat parameters as hypotheses—re-evaluate every 6 months and adjust.  
5. **Document:** Explain to the community why parameters look the way they do and how they behave.

**What the Forge framework should provide:**

1. Three reference-profiles (Research, Product, City) with documented parameters.  
2. Simulation tooling for pre-deployment parameter testing.  
3. Policy-layer guardrails against extreme settings.  
4. Tuning-oracles for data-driven parameter suggestions.

---

## Appendix A: Mathematical Analysis of the Red Queen Formula

### A.1 Stationary REP with Constant Activity

Given:

- Decay-rate: \(d\) (e.g. 0.05 for 5%)  
- Booster: \(\alpha\)  
- Activity: \(A\) (constant)  
- Community-average: \(C_{avg}\)

In the stationary state (REP no longer changes):

\[
REP_{new} = REP_{old}
\]

\[
REP \times (1 - d) + \alpha \times \frac{A}{C_{avg}} = REP
\]

\[
REP \times d = \alpha \times \frac{A}{C_{avg}}
\]

\[
REP_{stationary} = \frac{\alpha \times A}{d \times C_{avg}}
\]

**Interpretation:**  
The higher the decay, the higher your activity must be to maintain REP.

### A.2 Half-Life of REP Under Inactivity

For inactivity (\(A = 0\)):

\[
REP(t) = REP_0 \times (1 - d)^t
\]

Half-life ( \(REP(t) = 0.5 \times REP_0\) ):

\[
0.5 = (1 - d)^t \Rightarrow t = \frac{\ln(0.5)}{\ln(1 - d)}
\]

Examples:

- \(d = 0.02\) (2%): \(t \approx 34\) months  
- \(d = 0.05\) (5%): \(t \approx 14\) months  
- \(d = 0.08\) (8%): \(t \approx 8\) months  

---

## Appendix B: References & Further Reading

**Reputation Systems & Governance**

[5] Colony (2024). *Reputation-Based Voting in DAOs.*  
[6] Envisioning (2025). *Decentralized Identity & Reputation Systems.*  
[7] arXiv (2025). *DAO-AI: Evaluating Collective Decision-Making through Agentic AI.*

**Mechanism Design & Simulation**

[8] *Balancing the Scales: Ethical Frameworks for AI Agent Coordination* (2025).  
[9] Mesa: Agent-Based Modeling in Python – https://mesa.readthedocs.io

**Complex Systems & Social Dynamics**

[10] Ostrom, E. *Governing the Commons* (1990).  
[11] Axelrod, R. *The Evolution of Cooperation* (1984).

---

*Document Version: 1.0 — February 2026 — Tim Kosakatis — License: CC BY-SA 4.0 — Contact: tkosakatis@gmail.com* [file:2]
