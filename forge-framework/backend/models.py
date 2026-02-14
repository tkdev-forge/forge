from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String
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
    owneraddress: Mapped[str] = mapped_column(ForeignKey("members.address"), nullable=False)
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
