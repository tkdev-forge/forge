import base64
import hashlib
import hmac
import json
import time
from collections import defaultdict

from fastapi import Body, Depends, FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from agents.openclaw_client import OpenClawClient
from config import get_settings
from database import Base, engine, get_db
from economy.m2m_market import M2MMarketService
from governance.meta_dao import MetaDAOService
from models import Agent, Member, Trade
from reputation.agent_staking import deploy_agent_with_staking
from reputation.redqueen import apply_daily_rep_decay
from reputation.rli_oracle_client import RLIOracleClient, RLIRequest
from storage.ipfs_client import IPFSStorage


class SlowAPIRateLimiter:
    """Lightweight in-process limiter compatible with SlowAPI-style semantics."""

    def __init__(self, max_per_minute: int):
        self.max_per_minute = max_per_minute
        self.hits: dict[str, list[float]] = defaultdict(list)

    def enforce(self, key: str):
        now = time.time()
        window_start = now - 60
        self.hits[key] = [ts for ts in self.hits[key] if ts > window_start]
        if len(self.hits[key]) >= self.max_per_minute:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        self.hits[key].append(now)


settings = get_settings()
Base.metadata.create_all(bind=engine)
app = FastAPI(title=settings.app_name)
security = HTTPBearer(auto_error=False)
limiter = SlowAPIRateLimiter(settings.api_rate_limit_per_minute)
request_counter: dict[str, int] = defaultdict(int)


def _b64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def _decode_jwt(credentials: HTTPAuthorizationCredentials | None) -> dict:
    if not settings.jwt_required and credentials is None:
        return {"sub": "anonymous", "tier": 0}

    if credentials is None:
        raise HTTPException(status_code=401, detail="Missing bearer token")

    token = credentials.credentials
    try:
        header_b64, payload_b64, signature_b64 = token.split(".")
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Malformed token") from exc

    signed = f"{header_b64}.{payload_b64}".encode("utf-8")
    expected_sig = hmac.new(
        settings.jwt_secret.encode("utf-8"), signed, hashlib.sha256
    ).digest()
    token_sig = _b64url_decode(signature_b64)
    if not hmac.compare_digest(expected_sig, token_sig):
        raise HTTPException(status_code=401, detail="Invalid token")

    payload = json.loads(_b64url_decode(payload_b64))
    if "exp" in payload and int(payload["exp"]) < int(time.time()):
        raise HTTPException(status_code=401, detail="Token expired")
    return payload


def require_tier(min_tier: int):
    def _validator(
        credentials: HTTPAuthorizationCredentials | None = Depends(security),
    ):
        claims = _decode_jwt(credentials)
        tier = int(claims.get("tier", 0))
        if tier < min_tier:
            raise HTTPException(status_code=403, detail=f"Tier {min_tier}+ required")
        return claims

    return _validator


def mark_request(request: Request):
    ip = request.client.host if request.client else "unknown"
    limiter.enforce(ip)
    key = f"{request.method} {request.url.path}"
    request_counter[key] += 1


class DeployAgentRequest(BaseModel):
    owner_address: str
    agent_type: str
    stake_percentage: float = 0.15


class SpawnAgentRequest(DeployAgentRequest):
    config: dict = {}


class RLIRequestPayload(BaseModel):
    member: str
    task_id: str
    task_category: str
    deliverable_ipfs_hash: str


class ProposalRequest(BaseModel):
    proposer: str
    title: str
    body: str


class VoteRequest(BaseModel):
    proposal_id: int
    voter: str
    support: bool


class TradeRequest(BaseModel):
    buyer_agent: str
    seller_agent: str
    resource: str
    amount: float


@app.get("/")
def health(request: Request):
    mark_request(request)
    return {"status": "ok", "service": "forge-backend"}


@app.get("/health")
def healthz():
    return {"status": "healthy", "environment": settings.environment}


@app.get("/metrics")
def metrics(db: Session = Depends(get_db)):
    total_rep = db.query(func.coalesce(func.sum(Member.rep), 0.0)).scalar() or 0.0
    active_agents = db.query(Agent).filter(Agent.status == "active").count()
    total_trades = db.query(Trade).count()

    lines = [
        f'forge_requests_total{{endpoint="{k}"}} {v}'
        for k, v in request_counter.items()
    ]
    lines.extend(
        [
            f"forge_rep_total {float(total_rep)}",
            f"forge_agents_active {active_agents}",
            f"forge_trades_total {total_trades}",
        ]
    )
    return PlainTextResponse("\n".join(lines) + "\n")


@app.get("/agents")
def list_agents(
    request: Request, db: Session = Depends(get_db), _: dict = Depends(require_tier(1))
):
    mark_request(request)
    rows = db.query(Agent).all()
    return [
        {"agentid": a.agentid, "agenttype": a.agenttype, "status": a.status}
        for a in rows
    ]


@app.post("/agents/deploy")
def deploy_agent(
    request: Request,
    payload: DeployAgentRequest,
    db: Session = Depends(get_db),
    _: dict = Depends(require_tier(2)),
):
    mark_request(request)
    agent = deploy_agent_with_staking(
        db, payload.owner_address, payload.agent_type, payload.stake_percentage
    )
    return {
        "agentid": agent.agentid,
        "owner": agent.owneraddress,
        "staked_rep": agent.ownerrep,
    }


@app.post("/agents/spawn")
def spawn_agent(
    request: Request,
    payload: SpawnAgentRequest,
    db: Session = Depends(get_db),
    _: dict = Depends(require_tier(2)),
):
    mark_request(request)
    agent = deploy_agent_with_staking(
        db, payload.owner_address, payload.agent_type, payload.stake_percentage
    )
    result = OpenClawClient().spawn_agent(agent.agentid, payload.agent_type, payload.config)
    return {"agentid": agent.agentid, "status": agent.status, "runtime": result}


@app.post("/agents/{agent_id}/pause")
def pause_agent(
    agent_id: str,
    request: Request,
    db: Session = Depends(get_db),
    _: dict = Depends(require_tier(2)),
):
    mark_request(request)
    agent = db.query(Agent).filter(Agent.agentid == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="agent not found")
    agent.status = "paused"
    db.commit()
    return {"agentid": agent_id, "status": "paused", "runtime": OpenClawClient().pause_agent(agent_id)}


@app.post("/agents/{agent_id}/kill")
def kill_agent(
    agent_id: str,
    request: Request,
    db: Session = Depends(get_db),
    _: dict = Depends(require_tier(3)),
):
    mark_request(request)
    agent = db.query(Agent).filter(Agent.agentid == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="agent not found")
    agent.status = "killed"
    db.commit()
    return {"agentid": agent_id, "status": "killed", "runtime": OpenClawClient().kill_agent(agent_id)}


@app.get("/agents/{agent_id}/logs")
def agent_logs(agent_id: str, request: Request, _: dict = Depends(require_tier(1))):
    mark_request(request)
    return {"agentid": agent_id, "logs": OpenClawClient().get_agent_logs(agent_id)}


@app.post("/reputation/decay")
def trigger_decay(
    request: Request, db: Session = Depends(get_db), _: dict = Depends(require_tier(3))
):
    mark_request(request)
    changed = apply_daily_rep_decay(db)
    return {"updated_members": changed}


@app.post("/rli/request")
def request_rli(
    request: Request, payload: RLIRequestPayload, _: dict = Depends(require_tier(1))
):
    mark_request(request)
    client = RLIOracleClient()
    result = client.request_evaluation(
        RLIRequest(
            member=payload.member,
            task_id=payload.task_id,
            task_category=payload.task_category,
            deliverable_ipfs_hash=payload.deliverable_ipfs_hash,
        )
    )
    return result


@app.get("/rli/stats/{member}")
def rli_stats(member: str, request: Request, _: dict = Depends(require_tier(1))):
    mark_request(request)
    return {"member": member, "avg_automation": 0, "tasks": 0, "qualified": False}


@app.post("/storage/upload")
def storage_upload(
    request: Request,
    content: bytes = Body(..., media_type="application/octet-stream"),
    _: dict = Depends(require_tier(1)),
):
    mark_request(request)
    cid = IPFSStorage().upload(content)
    return {"cid": cid}


@app.get("/storage/{cid}")
def storage_download(cid: str, request: Request):
    mark_request(request)
    content = IPFSStorage().download(cid)
    return Response(content=content, media_type="application/octet-stream")


@app.post("/webhook/sms")
def sms_webhook(body: str = ""):
    approved = body.strip().upper() in {"YES", "Y", "APPROVE"}
    return {"approved": approved}


@app.get("/governance/proposals")
def list_governance_proposals(
    request: Request,
    status: str | None = None,
    db: Session = Depends(get_db),
    _: dict = Depends(require_tier(1)),
):
    mark_request(request)
    return MetaDAOService(db).list_proposals(status=status)


@app.post("/governance/proposals")
def create_governance_proposal(
    request: Request,
    payload: ProposalRequest,
    db: Session = Depends(get_db),
    _: dict = Depends(require_tier(2)),
):
    mark_request(request)
    try:
        return MetaDAOService(db).submit_proposal(payload.proposer, payload.title, payload.body)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/governance/vote")
def governance_vote(
    request: Request,
    payload: VoteRequest,
    db: Session = Depends(get_db),
    _: dict = Depends(require_tier(1)),
):
    mark_request(request)
    try:
        return MetaDAOService(db).vote(payload.proposal_id, payload.voter, payload.support)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/economy/trade/request")
def trade_request(
    request: Request,
    payload: TradeRequest,
    db: Session = Depends(get_db),
    _: dict = Depends(require_tier(1)),
):
    mark_request(request)
    svc = M2MMarketService(db)
    try:
        trade = svc.request_trade(
            payload.buyer_agent, payload.seller_agent, payload.resource, payload.amount
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "id": trade.id,
        "buyer_agent": trade.buyer_agent,
        "seller_agent": trade.seller_agent,
        "resource_type": trade.resource_type,
        "amount": trade.amount,
        "price": trade.price,
        "status": trade.status,
    }


@app.get("/economy/trades/{agent_id}")
def trade_list(
    agent_id: str,
    request: Request,
    db: Session = Depends(get_db),
    _: dict = Depends(require_tier(1)),
):
    mark_request(request)
    trades = M2MMarketService(db).list_trades_for_agent(agent_id)
    return [
        {
            "id": t.id,
            "buyer_agent": t.buyer_agent,
            "seller_agent": t.seller_agent,
            "resource_type": t.resource_type,
            "amount": t.amount,
            "price": t.price,
            "status": t.status,
        }
        for t in trades
    ]


@app.get("/economy/budget/{agent_id}")
def budget_get(
    agent_id: str,
    request: Request,
    db: Session = Depends(get_db),
    _: dict = Depends(require_tier(1)),
):
    mark_request(request)
    b = M2MMarketService(db).get_budget(agent_id)
    return {
        "agent_id": b.agent_id,
        "daily_limit": b.daily_limit,
        "weekly_limit": b.weekly_limit,
        "spent_today": b.spent_today,
        "spent_this_week": b.spent_this_week,
    }


@app.post("/meta/proposals")
def meta_proposal(
    request: Request,
    payload: ProposalRequest,
    db: Session = Depends(get_db),
    _: dict = Depends(require_tier(2)),
):
    mark_request(request)
    try:
        return MetaDAOService(db).submit_proposal(payload.proposer, payload.title, payload.body)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/meta/vote")
def meta_vote(
    request: Request,
    payload: VoteRequest,
    db: Session = Depends(get_db),
    _: dict = Depends(require_tier(1)),
):
    mark_request(request)
    try:
        return MetaDAOService(db).vote(payload.proposal_id, payload.voter, payload.support)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
