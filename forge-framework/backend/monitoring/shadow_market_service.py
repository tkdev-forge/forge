class ShadowMarketService:
    def signal(self, agent_id: str, score: float) -> dict:
        return {"agent_id": agent_id, "shadow_score": score, "action": "observe"}
