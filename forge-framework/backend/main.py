import base64
import hashlib
import hmac
import json
import time
from collections import defaultdict

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session

from config import get_settings
from database import Base, engine, get_db
from models import Agent
from reputation.agent_staking import deploy_agent_with_staking
from reputation.redqueen import apply_daily_rep_decay
from reputation.rli_oracle_client import RLIOracleClient, RLIRequest


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


class RLIRequestPayload(BaseModel):
    member: str
    task_id: str
    task_category: str
    deliverable_ipfs_hash: str


@app.get("/")
def health(request: Request):
    mark_request(request)
    return {"status": "ok", "service": "forge-backend"}


@app.get("/health")
def healthz():
    return {"status": "healthy", "environment": settings.environment}


@app.get("/metrics")
def metrics():
    lines = [
        f'forge_requests_total{{endpoint="{k}"}} {v}'
        for k, v in request_counter.items()
    ]
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


@app.post("/webhook/sms")
def sms_webhook(body: str = ""):
    approved = body.strip().upper() in {"YES", "Y", "APPROVE"}
    return {"approved": approved}


@app.post("/meta/proposals")
def meta_proposal(
    request: Request, title: str, body: str, _: dict = Depends(require_tier(2))
):
    mark_request(request)
    return {"status": "submitted", "title": title, "body": body}


@app.post("/meta/vote")
def meta_vote(
    request: Request,
    proposal_id: int,
    support: bool,
    _: dict = Depends(require_tier(1)),
):
    mark_request(request)
    return {"proposal_id": proposal_id, "support": support, "status": "recorded"}
