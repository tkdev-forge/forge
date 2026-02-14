from datetime import datetime

from sqlalchemy.orm import Session

from models import Member, RepHistory


def _tier_from_rep(rep: float) -> int:
    if rep >= 500:
        return 3
    if rep >= 100:
        return 2
    if rep >= 10:
        return 1
    return 0


def apply_daily_rep_decay(db: Session, daily_decay_rate: float = 0.0017) -> int:
    updated = 0
    members = db.query(Member).all()
    for m in members:
        old_rep = m.rep
        old_tier = m.tier
        m.rep = max(0.0, m.rep * (1 - daily_decay_rate))
        m.tier = _tier_from_rep(m.rep)
        updated += 1

        db.add(
            RepHistory(
                memberaddress=m.address,
                repchange=m.rep - old_rep,
                reason="daily_redqueen_decay",
                tierbefore=old_tier,
                tierafter=m.tier,
                timestamp=datetime.utcnow(),
            )
        )

    db.commit()
    return updated
