# RLI Integration Architecture

## Overview
RLI (Remote Labor Index) provides objective, human-evaluated quality metrics for agent work.

## Integration Components
1. Smart contract extension: `src/contracts/ForgeREP_RLI.sol`
2. Chainlink adapter: `src/backend/layers/layer6_reputation/rli_oracle.py`
3. API client: `src/backend/measurement/rli_client.py`

## Evaluation Protocol
1. Agent completes task and uploads to IPFS
2. Contract requests RLI evaluation
3. Oracle submits to RLI platform and polls result
4. Oracle fulfills on-chain metrics
5. REP awarded from automation rate, Elo, and value

## Cost & Performance
- Cost: $2.34 per evaluation
- Time: 11-17 minutes
- Evaluators: 3
