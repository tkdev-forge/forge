import pytest

from governance.meta_dao import MetaDAOService
from models import Member


def test_submit_proposal_shape(db_session):
    db_session.add(Member(address="0x1", name="Alice", rep=200, tier=2, role="member"))
    db_session.commit()

    svc = MetaDAOService(db_session)
    proposal = svc.submit_proposal("0x1", "Upgrade", "Enable stricter controls")

    assert proposal["status"] == "active"
    assert proposal["title"] == "Upgrade"
    assert proposal["body"] == "Enable stricter controls"


def test_submit_proposal_requires_tier(db_session):
    db_session.add(Member(address="0x2", name="Bob", rep=5, tier=0, role="member"))
    db_session.commit()

    svc = MetaDAOService(db_session)
    with pytest.raises(ValueError):
        svc.submit_proposal("0x2", "", "")
