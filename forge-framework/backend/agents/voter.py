class VoterAgent:
    def vote(self, proposal_id: int, support: bool) -> dict:
        return {"proposal_id": proposal_id, "support": support}
