```markdown
# Forge Framework V4 🛠️

**Universal, host-agnostic OS for scalable Human-AI collaboration.**  
From 3-5 founders to 100k agents across 100 projects. 11-Layer architecture with Red Queen REP (decay + boosts), shared REP staking, tiered access (0-3), M2M economy, ZK privacy, prediction markets & per-project L3 rollups. [file:5]

## Layers Diagram
```mermaid
graph TD
    A[Layer 1: Access<br/>DID/REP Gates] --> B[Layer 2: Agent Core<br/>OpenClaw Sandbox]
    B --> C[Layer 3: Communication<br/>Pi Protocol MQTT]
    C --> D[Layer 4: M2M Economy<br/>Tier-Limits Trades]
    D --> E[Layer 5: Governance<br/>DAO REP-Votes]
    E --> F[Layer 6: Reputation<br/>Red Queen ERC-5192]
    F --> G[Layer 7: Storage<br/>PostgreSQL IPFS]
    G --> H[Layer 8: Infrastructure<br/>K8s Hetzner]
    H --> I[Layer 9: Monitoring<br/>Rogue 92% Markets]
    I --> J[L10: Meta-Economy<br/>REP Bridges]
    J --> K[L11: L3 Rollups<br/>Arbitrum Orbit]
    
    style A fill:#e1f5fe
    style K fill:#c8e6c9
```mermaid

## Core Features

- **Layered Architecture**: 11 layers (Access, Agents, REP, Economy, Governance → L3).
- **Red Queen REP**: 5%/month decay, activity boosts vs. community avg.
- **Tier System**: REP → Tiers (0: Guest, 3: Root w/ killswitch).
- **M2M Economy**: Tier-limited trades (energy/compute/data).
- **Federated Multi-Project**: Cross-chain REP bridges, meta-governance.
- **Security**: Rogue detection (92% via markets), auto-pause, multisig.

| Tier | Min REP | Capabilities |
|------|---------|--------------|
| 0    | 0       | Read-only    |
| 1    | 10      | Basic agents |
| 2    | 100     | Vote, budget |
| 3    | 500     | Killswitch   | 

## Quickstart (Genesis Phase)

1. **Setup Infra**: Hetzner nodes, PostgreSQL, OpenClaw gateway.
2. **Deploy Genesis Agent** (500 LOC Python): Mint contracts on Optimism.
3. **Bootstrap Governance**: REP-weighted vote on policies.

```bash
pip install openclaw web3 psycopg2
python backend/genesis/genesis-agent.py  # Deploys DAO/REP
```

## Tech Stack

- **Agents**: OpenClaw (multi-agent runtime).
- **Blockchain**: Optimism L2, Arbitrum Orbit L3.
- **Contracts**: Solidity (ForgeREP.sol, MetaBridge.sol).
- **Backend**: Python/FastAPI, PostgreSQL.
- **Monitoring**: Prometheus + Market Signals.

## Docs

**English Markdown**

- [V4 Full EN](docs/en/forge-v4-full-en.md)
- [V3.3 Full EN](docs/en/forge-v3.3-full-en.md)
- [V3.2 Full EN](docs/en/forge-v3.2-full-en.md)

**Other**

- [Deployment Examples](docs/deployment/)
- [Socio-Technical Parameters (V3)](docs/en/forge-v3-socio-technical-parameters.md)

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)  
[![Stars](https://img.shields.io/github/stars/tkdev-forge/forge?style=social)](https://github.com/tkdev-forge/forge/stargazers)

**Keywords**: ai-agents, dao, rep, m2m, l3-rollup, openclaw
```
