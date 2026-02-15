import pytest
from src.backend.layers.layer6_reputation.rli_oracle import RLIPerformanceOracle


@pytest.mark.asyncio
async def test_rli_evaluation_flow():
    oracle = RLIPerformanceOracle()
    result = await oracle.handle_evaluation_request("req-1", "0xabc", "ipfs://hash")
    assert 0 <= result.automation_rate <= 1.0
    assert result.elo_score > 0
