from backend.governance.meta_dao import MetaDAOService


def test_submit_proposal_shape():
    svc = MetaDAOService()
    proposal = svc.submit_proposal("Upgrade", "Enable stricter controls")

    assert proposal["status"] == "submitted"
    assert proposal["title"] == "Upgrade"
    assert proposal["body"] == "Enable stricter controls"


def test_submit_proposal_empty_values_allowed_for_backwards_compatibility():
    svc = MetaDAOService()
    proposal = svc.submit_proposal("", "")

    assert proposal == {"status": "submitted", "title": "", "body": ""}
