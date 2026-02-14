from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from models import Agent, AgentBudget, Trade


class M2MMarketService:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def quote(resource: str, amount: float) -> float:
        base = {
            "compute": 0.04,
            "energy": 0.01,
            "data": 0.02,
            "api_call": 0.03,
            "storage": 0.015,
        }.get(resource, 0.05)
        return round(base * amount, 6)

    def _ensure_budget(self, agent_id: str) -> AgentBudget:
        budget = self.db.query(AgentBudget).filter(AgentBudget.agent_id == agent_id).first()
        if budget:
            return budget
        budget = AgentBudget(agent_id=agent_id)
        self.db.add(budget)
        self.db.commit()
        self.db.refresh(budget)
        return budget

    def _refresh_budget_windows(self, budget: AgentBudget):
        now = datetime.utcnow()
        if now - budget.last_reset_daily >= timedelta(days=1):
            budget.spent_today = 0
            budget.last_reset_daily = now
        if now - budget.last_reset_weekly >= timedelta(days=7):
            budget.spent_this_week = 0
            budget.last_reset_weekly = now

    def request_trade(
        self, buyer_agent: str, seller_agent: str, resource: str, amount: float
    ) -> Trade:
        buyer = self.db.query(Agent).filter(Agent.agentid == buyer_agent).first()
        seller = self.db.query(Agent).filter(Agent.agentid == seller_agent).first()
        if not buyer or not seller:
            raise ValueError("buyer or seller agent not found")

        price = self.quote(resource, amount)
        budget = self._ensure_budget(buyer_agent)
        self._refresh_budget_windows(budget)

        if budget.spent_today + price > budget.daily_limit:
            raise ValueError("daily budget exceeded")
        if budget.spent_this_week + price > budget.weekly_limit:
            raise ValueError("weekly budget exceeded")

        budget.spent_today += price
        budget.spent_this_week += price

        trade = Trade(
            buyer_agent=buyer_agent,
            seller_agent=seller_agent,
            resource_type=resource,
            amount=amount,
            price=price,
            status="requested",
        )
        self.db.add(trade)
        self.db.commit()
        self.db.refresh(trade)
        return trade

    def list_trades_for_agent(self, agent_id: str) -> list[Trade]:
        return (
            self.db.query(Trade)
            .filter((Trade.buyer_agent == agent_id) | (Trade.seller_agent == agent_id))
            .order_by(Trade.id.desc())
            .all()
        )

    def get_budget(self, agent_id: str) -> AgentBudget:
        budget = self._ensure_budget(agent_id)
        self._refresh_budget_windows(budget)
        self.db.commit()
        self.db.refresh(budget)
        return budget
