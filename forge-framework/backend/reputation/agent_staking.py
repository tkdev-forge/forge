import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from models import Agent, Member, RepHistory


def deploy_agent_with_staking(db: Session, owner_address: str, agent_type: str, stake_percentage: float = 0.15) -> Agent:
    owner = db.query(Member).filter(Member.address == owner_address).first()
    if not owner:
        raise ValueError("owner not found")

    if stake_percentage < 0 or stake_percentage > 1:
        raise ValueError("stake_percentage must be between 0 and 1")

    stake = owner.rep * stake_percentage
    tier_before = owner.tier
    owner.rep = max(0.0, owner.rep - stake)

    if owner.rep >= 500:
        owner.tier = 3
    elif owner.rep >= 100:
        owner.tier = 2
    elif owner.rep >= 10:
        owner.tier = 1
    else:
        owner.tier = 0

    agent = Agent(
        agentid=f"agent-{uuid.uuid4()}",
        agenttype=agent_type,
        owneraddress=owner_address,
        ownerrep=stake,
        tier=owner.tier,
        status="active",
        createdat=datetime.utcnow(),
        lastheartbeat=datetime.utcnow(),
    )
    db.add(agent)

    db.add(
        RepHistory(
            memberaddress=owner_address,
            agentid=agent.agentid,
            repchange=-stake,
            reason="agent_staking",
            tierbefore=tier_before,
            tierafter=owner.tier,
        )
    )

    db.commit()
    db.refresh(agent)
    return agent
