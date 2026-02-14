# RLI Integration for Forge Framework

## Overview

**RLI (Remote Labor Index)** is an objective benchmark for measuring AI agent performance on real, economically valuable tasks. This integration adds RLI evaluation capabilities to the Forge Framework, enabling:

- **Objective performance metrics** for REP allocation
- **Tier qualification gates** based on proven capability
- **Quality-based agent advancement** beyond subjective reviews
- **Market validation** for M2M economy pricing

## Why RLI?

Forge V3.2/V3.3 uses **Red Queen Reputation** based on contributions (code commits, governance votes, etc.)[cite:5]. While this works well, it lacks:

1. **Objective quality measurement** - A bad PR merged still earns REP
2. **Task complexity weighting** - All contributions treated equally
3. **Real-world validation** - No connection to economic value

RLI solves this by:
- **240 real freelance projects** worth $140k+ in actual work[file:1]
- **Human evaluators** comparing AI vs. human deliverables
- **Automation Rate** (0-100%) + **Elo score** (relative to human baseline)
- **Economic value tracking** for REP calculation

## Architecture

### Layer 6.1: RLI Oracle Extension

RLI integrates as **Layer 6.1** - an optional extension to the existing Reputation layer:

```
Layer 6: Reputation (ForgeREP.sol)
  ├── Red Queen Decay (5%/month)
  ├── Activity Boost (relative to community avg)
  └── Layer 6.1: RLI Oracle ← NEW
      ├── Chainlink integration
      ├── IPFS deliverable storage
      └── Tier qualification checks
```

### Components

1. **Smart Contract** (`contracts/extensions/ForgeREP_RLI.sol`)
   - Stores RLI evaluation results on-chain
   - Tracks per-member automation rates, Elo scores, task counts
   - Gates tier upgrades based on RLI thresholds

2. **Oracle Backend** (`backend/layers/layer6-reputation/rli/rli_oracle.py`)
   - Chainlink External Adapter
   - Submits agent deliverables to RLI Platform
   - Polls for evaluation results
   - Fulfills on-chain requests

3. **Database Schema** (`migrations/002_rli_extensions.sql`)
   - `rli_evaluations` table for tracking results
   - `rli_task_queue` for pending evaluations
   - Extends `agents` table with RLI stats

## Tier Requirements

| Tier | Min REP | RLI Requirements |
|------|---------|------------------|
| 0 (Guest) | 0 | None |
| 1 (Developer) | 10 | None |
| 2 (Senior) | 100 | ≥50% automation on 3 tasks, Elo ≥800 |
| 3 (CTO/Root) | 500 | ≥70% automation on 5 tasks, Elo ≥1000 |

### Example Flow

```
1. Developer (Tier 1, 120 REP) wants to deploy advanced agent
2. System checks: REP ≥100 ✓, Tier 2 requires RLI ✗
3. Developer completes 3 RLI benchmark tasks:
   - Task 1: Web dev (React dashboard) → 65% automation, Elo 850
   - Task 2: Data viz (Python plots) → 72% automation, Elo 920
   - Task 3: Documentation (LaTeX report) → 58% automation, Elo 800
4. Average automation: 65% ✓ (≥50%)
5. Max Elo: 920 ✓ (≥800)
6. Tasks completed: 3 ✓ (≥3)
7. System grants Tier 2 qualification
8. Developer can now deploy advanced agents
```

## Cost Structure

- **Cost per evaluation**: $2.34 USD (11-17 min human evaluation)[file:1]
- **Initial budget**: 100 evaluations = $234
- **Auto-replenish**: Triggers at <20 remaining
- **Optimization**: Only required for Tier 2→3 upgrades (not every REP transaction)

### Cost Projection

| Users | Tier 2+ Rate | Evals/Year | Annual Cost |
|-------|-------------|------------|-------------|
| 50 | 20% (10) | 30 | $70 |
| 500 | 20% (100) | 300 | $702 |
| 5000 | 20% (1000) | 3000 | $7,020 |

## Integration Points

### 1. Agent Deployment Gate

```python
# backend/layers/layer2-core/agent_deployment.py

async def deploy_agent_with_rli_gate(owner, agent_type, stake_percentage=0.15):
    owner_tier = get_tier(owner.address)
    agent_tier = calculate_agent_tier(owner_tier, agent_type)
    
    # NEW: RLI check for Tier 2+
    if agent_tier >= 2:
        can_upgrade, reason = await check_rli_qualification(
            owner.address,
            target_tier=agent_tier
        )
        if not can_upgrade:
            raise RLIQualificationError(f"RLI required: {reason}")
    
    # ... existing deployment logic ...
```

### 2. REP Allocation

```python
# RLI evaluation automatically awards REP

def calculate_rep_from_rli(automation_rate, elo_score, economic_value):
    # Base REP: 10% of economic value scaled by automation rate
    base_rep = (automation_rate * economic_value * 0.1)
    
    # Elo bonus for exceeding human baseline (1000)
    elo_bonus = max(0, (elo_score - 1000) / 10)
    
    return base_rep + elo_bonus

# Example:
# - Task: $200 web development project
# - Automation: 80%
# - Elo: 1100
# → REP = (0.8 × 200 × 0.1) + (100/10) = 16 + 10 = 26 REP
```

### 3. Monitoring Integration (Phase 2)

RLI scores feed into Layer 9 Monitoring:

```python
# Federated Auditor uses RLI as quality signal

combined_risk = (
    0.60 × hard_signals +      # Transaction patterns
    0.30 × rli_quality_drop +  # RLI performance degradation
    0.10 × shadow_markets      # Prediction market signals
)

if combined_risk > 0.8:
    auto_pause_agent()
```

## Setup Guide

### Prerequisites

1. **RLI Platform Access**
   - Contact: https://github.com/centerforaisafety/rli_evaluation_platform
   - API token required

2. **Chainlink Node**
   - Deploy Chainlink node or use existing
   - Create External Adapter job

3. **IPFS Pinning**
   - Pinata/Infura account for deliverable storage

### Deployment Steps

#### 1. Deploy Smart Contract

```bash
cd contracts
npm install

# Deploy to testnet (Optimism Sepolia)
npx hardhat run scripts/deploy-rli-extension.js --network optimism-sepolia

# Output: Contract address for ForgeREP_RLI
```

#### 2. Setup Oracle Backend

```bash
cd backend
pip install -r requirements.txt

# Configure environment
cp .env.example .env

# Edit .env:
# RLI_PLATFORM_URL=https://rli-eval.forge.network
# RLI_ADMIN_TOKEN=<your_token>
# FORGE_REP_RLI_CONTRACT=<deployed_address>
# CHAINLINK_NODE_URL=http://localhost:6688

# Run oracle server
python -m layers.layer6_reputation.rli.rli_oracle
```

#### 3. Run Database Migration

```bash
psql -U forge -d forge_db -f migrations/002_rli_extensions.sql
```

#### 4. Update Configuration

```bash
# Edit config/rli/rli-oracle.json
# Update oracle_address, job_id after Chainlink setup
```

#### 5. Test Integration

```bash
pytest tests/unit/test_rli_oracle.py
pytest tests/integration/test_rli_flow_e2e.py
```

## API Reference

### Smart Contract

```solidity
// Request RLI evaluation
function requestRLIEvaluation(
    address member,
    uint256 taskId,
    string calldata taskCategory,
    string calldata deliverableIPFSHash
) external returns (bytes32 requestId);

// Check tier qualification
function canUpgradeToTier(
    address member,
    uint8 targetTier
) public view returns (bool qualified, string memory reason);

// Get RLI stats
function getRLIStats(address member) external view returns (
    uint256 tasksCompleted,
    uint256 avgAutomation,
    uint256 maxElo,
    bool tierQualified
);
```

### Python Backend

```python
from backend.layers.layer6_reputation.rli.rli_oracle import RLIPerformanceOracle

oracle = RLIPerformanceOracle(...)

# Submit evaluation request
result = await oracle.handle_evaluation_request(
    request_id="0x123...",
    member_address="0xABC...",
    task_id=42,
    task_category="web-development",
    deliverable_ipfs_hash="Qm..."
)

print(f"Automation: {result.automation_rate:.1%}")
print(f"Elo: {result.elo_score}")
```

## Troubleshooting

### Common Issues

1. **"Budget exhausted" error**
   - Check `rli_budget` table: `SELECT * FROM rli_budget;`
   - Replenish: `UPDATE rli_budget SET total_budget = total_budget + 100;`

2. **Chainlink request timeout**
   - RLI evaluations take 11-17 minutes[file:1]
   - Check oracle logs: `docker logs rli-oracle`
   - Verify Chainlink node connectivity

3. **IPFS upload fails**
   - Check Pinata API key in config
   - Verify file size <100MB
   - Try alternative gateway

4. **Tier qualification not updating**
   - Check `agents` table: `SELECT agentid, rli_avg_automation, rli_tasks_completed FROM agents WHERE owneraddress='0x...';`
   - Verify trigger is enabled: `SELECT * FROM pg_trigger WHERE tgname='trg_update_rli_stats';`

## Roadmap

### Phase 1: Foundation ✅ (Current)
- [x] Smart contract extension
- [x] Oracle backend
- [x] Database schema
- [x] Tier qualification gates

### Phase 2: Monitoring (Next)
- [ ] Integrate with FederatedAuditor (Layer 9.2)
- [ ] RLI quality degradation alerts
- [ ] Prometheus metrics export

### Phase 3: Optimization
- [ ] Batch evaluation requests
- [ ] Cached RLI benchmarks
- [ ] Predictive tier qualification (ML)

### Phase 4: Expansion
- [ ] Custom RLI task sets per domain
- [ ] Community-submitted benchmarks
- [ ] Multi-chain RLI attestations

## References

- [RLI Paper (arXiv:2510.26787)](https://arxiv.org/abs/2510.26787)[file:1]
- [RLI Platform (GitHub)](https://github.com/centerforaisafety/rli_evaluation_platform)[cite:8]
- [Forge V3.3 Documentation](../en/forge-v3.3-full-en.md)[file:5]
- [Chainlink External Adapters](https://docs.chain.link/chainlink-nodes/external-adapters/external-adapters)

## Support

- GitHub Issues: [tkdev-forge/forge/issues](https://github.com/tkdev-forge/forge/issues)
- Discord: (Add link)
- Email: (Add contact)
