class GenesisAgent:
    def bootstrap(self, profile: str, founders: list[str]) -> dict:
        return {"profile": profile, "founders": founders, "status": "bootstrapped"}
