import os

import httpx


class OpenClawClient:
    def __init__(self):
        self.base_url = os.getenv("OPENCLAW_GATEWAY_URL", "http://openclaw-gateway:8001")
        self.timeout = float(os.getenv("OPENCLAW_TIMEOUT_SEC", "5"))

    def _post(self, path: str, payload: dict) -> dict:
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(f"{self.base_url}{path}", json=payload)
                resp.raise_for_status()
                return resp.json()
        except Exception as exc:
            return {"status": "gateway_unavailable", "detail": str(exc)}

    def spawn_agent(self, agent_id: str, agent_type: str, config: dict) -> dict:
        return self._post(
            "/agents/spawn",
            {"agent_id": agent_id, "agent_type": agent_type, "config": config},
        )

    def pause_agent(self, agent_id: str) -> dict:
        return self._post(f"/agents/{agent_id}/pause", {})

    def kill_agent(self, agent_id: str) -> dict:
        return self._post(f"/agents/{agent_id}/kill", {})

    def get_agent_logs(self, agent_id: str) -> list[str]:
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.get(f"{self.base_url}/agents/{agent_id}/logs")
                resp.raise_for_status()
                data = resp.json()
                return data.get("logs", [])
        except Exception:
            return []
