import base64
import hashlib
import hmac
import json
import time

from models import Agent, Member


def _token(tier: int) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {"sub": "tester", "tier": tier, "exp": int(time.time()) + 3600}

    def _enc(obj):
        raw = json.dumps(obj, separators=(",", ":")).encode("utf-8")
        return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("utf-8")

    h = _enc(header)
    p = _enc(payload)
    sig = hmac.new(b"dev-secret-change-me", f"{h}.{p}".encode("utf-8"), hashlib.sha256).digest()
    s = base64.urlsafe_b64encode(sig).rstrip(b"=").decode("utf-8")
    return f"{h}.{p}.{s}"


def test_health_and_metrics(client):
    health = client.get("/health")
    assert health.status_code == 200

    metrics = client.get("/metrics")
    assert metrics.status_code == 200
    assert "forge_rep_total" in metrics.text


def test_governance_endpoints(client, db_session):
    db_session.add(Member(address="0xproposer", name="P", rep=300, tier=3, role="member"))
    db_session.add(Member(address="0xvoter", name="V", rep=20, tier=1, role="member"))
    db_session.commit()

    headers_t2 = {"Authorization": f"Bearer {_token(2)}"}
    proposal = client.post(
        "/governance/proposals",
        json={"proposer": "0xproposer", "title": "T", "body": "B"},
        headers=headers_t2,
    )
    assert proposal.status_code == 200
    pid = proposal.json()["id"]

    headers_t1 = {"Authorization": f"Bearer {_token(1)}"}
    vote = client.post(
        "/governance/vote",
        json={"proposal_id": pid, "voter": "0xvoter", "support": True},
        headers=headers_t1,
    )
    assert vote.status_code == 200
    assert vote.json()["votes_for"] == 1


def test_economy_endpoints(client, db_session):
    db_session.add(Member(address="0xowner", name="Owner", rep=1000, tier=3, role="member"))
    db_session.add_all(
        [
            Agent(agentid="agent-a", agenttype="echo", owneraddress="0xowner", ownerrep=10, tier=1),
            Agent(agentid="agent-b", agenttype="echo", owneraddress="0xowner", ownerrep=10, tier=1),
        ]
    )
    db_session.commit()

    headers_t1 = {"Authorization": f"Bearer {_token(1)}"}
    resp = client.post(
        "/economy/trade/request",
        json={
            "buyer_agent": "agent-a",
            "seller_agent": "agent-b",
            "resource": "compute",
            "amount": 10,
        },
        headers=headers_t1,
    )
    assert resp.status_code == 200

    trades = client.get("/economy/trades/agent-a", headers=headers_t1)
    assert trades.status_code == 200
    assert len(trades.json()) == 1

    budget = client.get("/economy/budget/agent-a", headers=headers_t1)
    assert budget.status_code == 200
    assert budget.json()["spent_today"] > 0
