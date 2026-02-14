from sqlalchemy.orm import Session

from models import Member, Proposal


class MetaDAOService:
    def __init__(self, db: Session):
        self.db = db

    def submit_proposal(self, proposer: str, title: str, body: str) -> dict:
        member = self.db.query(Member).filter(Member.address == proposer).first()
        if not member or member.tier < 2:
            raise ValueError("proposer tier too low")

        proposal = Proposal(title=title, body=body, proposer=proposer, status="active")
        self.db.add(proposal)
        self.db.commit()
        self.db.refresh(proposal)
        return self._serialize(proposal)

    def list_proposals(self, status: str | None = None) -> list[dict]:
        query = self.db.query(Proposal)
        if status:
            query = query.filter(Proposal.status == status)
        return [self._serialize(p) for p in query.order_by(Proposal.id.desc()).all()]

    def vote(self, proposal_id: int, voter: str, support: bool) -> dict:
        member = self.db.query(Member).filter(Member.address == voter).first()
        if not member or member.tier < 1:
            raise ValueError("voter tier too low")
        proposal = self.db.query(Proposal).filter(Proposal.id == proposal_id).first()
        if not proposal:
            raise ValueError("proposal not found")

        if support:
            proposal.votes_for += 1
        else:
            proposal.votes_against += 1
        self.db.commit()
        self.db.refresh(proposal)
        return self._serialize(proposal)

    @staticmethod
    def _serialize(proposal: Proposal) -> dict:
        return {
            "id": proposal.id,
            "title": proposal.title,
            "body": proposal.body,
            "proposer": proposal.proposer,
            "status": proposal.status,
            "votes_for": proposal.votes_for,
            "votes_against": proposal.votes_against,
        }
