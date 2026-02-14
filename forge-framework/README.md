# Forge Framework V4 + RLI

Full-stack reference implementation for the Forge 11-layer human-AI collaboration OS.

## Quick start

1. Copy env file:
   ```bash
   cp .env.example .env
   ```
2. Start backend + infra:
   ```bash
   docker-compose up --build
   ```
3. Install and deploy contracts:
   ```bash
   cd contracts
   npm install
   npx hardhat run scripts/deploy.js --network sepolia
   ```

## Production readiness updates

- FastAPI now supports JWT-based auth, REP-tier endpoint protection, rate limiting, and `/health` + `/metrics` endpoints.
- Foundry test and deploy workflow added for `ForgeREP` (including gas report + Optimism Sepolia-compatible script).
- CI checks include `pytest`, `black`, `forge test --gas-report`, and Slither high-severity fail gates.
- Use `.env.example` + pydantic settings validation for environment sanity.

## Layers implemented

- L0: Genesis bootstrap (`backend/agents/genesisagent.py`, `scripts/genesis-select-profile.py`)
- L1/L1.1: API + optional ZK REP verifier
- L2/L3: Agent core + Pi-style message payloads
- L4: M2M escrow and backend market service
- L5/L5.1: REP governance + prediction markets
- L6/L6.1: Red Queen REP + RLI extension
- L7: PostgreSQL schema + SQL files
- L8/L9/L9.1: Docker infra + monitoring/shadow service hooks
- L10/L11: Meta-REP bridge + L3 rollup manager

## Notes

- ZK, oracle, and cross-chain paths are scaffolded for extension.
- Contracts are intentionally minimal and auditable for MVP usage.
