class HumanLoopAgent:
    def parse_reply(self, body: str) -> bool:
        return body.strip().upper() in {"YES", "Y", "APPROVE"}
