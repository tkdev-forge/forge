class M2MMarketService:
    def quote(self, resource: str, amount: float) -> float:
        base = {"compute": 0.04, "energy": 0.01, "data": 0.02}.get(resource, 0.05)
        return round(base * amount, 6)
