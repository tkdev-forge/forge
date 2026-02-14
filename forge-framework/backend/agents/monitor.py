class MonitorAgent:
    def heartbeat(self, agent_id: str) -> dict:
        return {"agent_id": agent_id, "alive": True}
