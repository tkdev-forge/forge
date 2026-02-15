# Forge PoC Architecture

Forge is a **multi-layer measurement system** for agent efficiency benchmarking.

## Core Innovation: RLI Integration

1. Agent completes task
2. Deliverable uploaded to IPFS
3. Chainlink Oracle triggers RLI Platform
4. 3 human evaluators score vs human baseline
5. Oracle returns: Automation Rate, Elo Score
6. Smart contract awards REP proportional to quality
7. All metrics logged for analysis

## Key Components
- Smart Contract: `src/contracts/ForgeREP_RLI.sol`
- Backend Tracker: `src/backend/measurement/efficiency_tracker.py`
- Frontend Dashboard: `src/frontend/research-dashboard`

## Data Flow
Task Assignment → Agent Execution → IPFS Upload → RLI Oracle Request → Human Evaluation → Oracle Fulfillment → REP Update + Metrics Storage → Dashboard Update
