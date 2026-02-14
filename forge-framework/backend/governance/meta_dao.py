class MetaDAOService:
    def submit_proposal(self, title: str, body: str) -> dict:
        return {"status": "submitted", "title": title, "body": body}
