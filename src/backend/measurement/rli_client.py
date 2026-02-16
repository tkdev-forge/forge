"""RLI platform API client interface for PoC."""

from src.backend.measurement.interfaces import RLIEvaluation, RLIClientInterface


class RLIPlatformClient(RLIClientInterface):
    async def create_comparison(self, ai_deliverable: str, human_baseline: str, task_brief: str) -> str:
        return "comparison-placeholder"

    async def get_evaluation_result(self, comparison_id: str) -> RLIEvaluation:
        return RLIEvaluation(
            automation_rate=0.75,
            elo_score=920,
            economic_value=200.0,
            comparison_url=f"https://rli-eval.forge.network/results/{comparison_id}",
        )
