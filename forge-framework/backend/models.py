from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Member(Base):
    __tablename__ = "members"

    address: Mapped[str] = mapped_column(String(128), primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    rep: Mapped[float] = mapped_column(Float, default=0)
    tier: Mapped[int] = mapped_column(Integer, default=0)
    role: Mapped[str] = mapped_column(String(64), default="member")


class Agent(Base):
    __tablename__ = "agents"

    agentid: Mapped[str] = mapped_column(String(128), primary_key=True)
    agenttype: Mapped[str] = mapped_column(String(64), nullable=False)
    owneraddress: Mapped[str] = mapped_column(
        ForeignKey("members.address"), nullable=False
    )
    ownerrep: Mapped[float] = mapped_column(Float, default=0)
    tier: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(32), default="active")
    createdat: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    lastheartbeat: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    isrogue: Mapped[bool] = mapped_column(Boolean, default=False)
    shadowrepactive: Mapped[bool] = mapped_column(Boolean, default=False)


class RepHistory(Base):
    __tablename__ = "rep_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    memberaddress: Mapped[str] = mapped_column(String(128), nullable=False)
    agentid: Mapped[str | None] = mapped_column(String(128), nullable=True)
    repchange: Mapped[float] = mapped_column(Float, nullable=False)
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    tierbefore: Mapped[int] = mapped_column(Integer, default=0)
    tierafter: Mapped[int] = mapped_column(Integer, default=0)
    txhash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Proposal(Base):
    __tablename__ = "proposals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    proposer: Mapped[str] = mapped_column(ForeignKey("members.address"), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="active")
    votes_for: Mapped[int] = mapped_column(Integer, default=0)
    votes_against: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    execution_tx: Mapped[str | None] = mapped_column(String(128), nullable=True)


class Trade(Base):
    __tablename__ = "trades"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    buyer_agent: Mapped[str] = mapped_column(ForeignKey("agents.agentid"), nullable=False)
    seller_agent: Mapped[str] = mapped_column(ForeignKey("agents.agentid"), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(32), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="requested")
    escrow_tx: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class AgentBudget(Base):
    __tablename__ = "agent_budgets"

    agent_id: Mapped[str] = mapped_column(ForeignKey("agents.agentid"), primary_key=True)
    daily_limit: Mapped[float] = mapped_column(Float, default=100.0)
    weekly_limit: Mapped[float] = mapped_column(Float, default=500.0)
    spent_today: Mapped[float] = mapped_column(Float, default=0.0)
    spent_this_week: Mapped[float] = mapped_column(Float, default=0.0)
    last_reset_daily: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_reset_weekly: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
