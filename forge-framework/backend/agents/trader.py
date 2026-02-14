class TraderAgent:
    def execute(self, market: str, amount: float) -> dict:
        return {"market": market, "amount": amount, "status": "submitted"}
