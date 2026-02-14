import pytest

from economy.m2m_market import M2MMarketService
from models import Agent, Member


def _seed_agents(db_session):
    db_session.add_all(
        [
            Member(address="0xowner", name="Owner", rep=1000, tier=3, role="member"),
            Agent(agentid="agent-a", agenttype="echo", owneraddress="0xowner", ownerrep=10, tier=1),
            Agent(agentid="agent-b", agenttype="echo", owneraddress="0xowner", ownerrep=10, tier=1),
        ]
    )
    db_session.commit()


@pytest.mark.parametrize(
    ("resource", "amount", "expected"),
    [
        ("compute", 10, 0.4),
        ("energy", 10, 0.1),
        ("data", 10, 0.2),
        ("unknown", 10, 0.5),
        ("compute", 0, 0.0),
    ],
)
def test_quote_by_resource(resource: str, amount: float, expected: float):
    assert M2MMarketService.quote(resource, amount) == expected


def test_trade_request_and_budget(db_session):
    _seed_agents(db_session)
    svc = M2MMarketService(db_session)
    trade = svc.request_trade("agent-a", "agent-b", "compute", 10)

    assert trade.price == 0.4
    budget = svc.get_budget("agent-a")
    assert budget.spent_today == 0.4


def test_trade_rejects_daily_budget_exceeded(db_session):
    _seed_agents(db_session)
    svc = M2MMarketService(db_session)
    svc.get_budget("agent-a").daily_limit = 0.2
    db_session.commit()

    with pytest.raises(ValueError):
        svc.request_trade("agent-a", "agent-b", "compute", 10)
