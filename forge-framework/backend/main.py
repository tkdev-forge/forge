from fastapi import Depends, FastAPI
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import Agent
from reputation.agent_staking import deploy_agent_with_staking
from reputation.redqueen import apply_daily_rep_decay
from reputation.rli_oracle_client import RLIOracleClient, RLIRequest

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Forge Framework API")


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
def health():
    return {"status": "ok", "service": "forge-backend"}


@app.get("/agents")
def list_agents(db: Session = Depends(get_db)):
    rows = db.query(Agent).all()
    return [{"agentid": a.agentid, "agenttype": a.agenttype, "status": a.status} for a in rows]


@app.post("/agents/deploy")
def deploy_agent(payload: DeployAgentRequest, db: Session = Depends(get_db)):
    agent = deploy_agent_with_staking(db, payload.owner_address, payload.agent_type, payload.stake_percentage)
    return {"agentid": agent.agentid, "owner": agent.owneraddress, "staked_rep": agent.ownerrep}


@app.post("/reputation/decay")
def trigger_decay(db: Session = Depends(get_db)):
    changed = apply_daily_rep_decay(db)
    return {"updated_members": changed}


@app.post("/rli/request")
def request_rli(payload: RLIRequestPayload):
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
def rli_stats(member: str):
    return {"member": member, "avg_automation": 0, "tasks": 0, "qualified": False}


@app.post("/webhook/sms")
def sms_webhook(body: str = ""):
    approved = body.strip().upper() in {"YES", "Y", "APPROVE"}
    return {"approved": approved}


@app.post("/meta/proposals")
def meta_proposal(title: str, body: str):
    return {"status": "submitted", "title": title, "body": body}


@app.post("/meta/vote")
def meta_vote(proposal_id: int, support: bool):
    return {"proposal_id": proposal_id, "support": support, "status": "recorded"}
