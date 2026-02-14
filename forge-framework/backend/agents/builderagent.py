class BuilderAgent:
    def build_spa(self, prompt: str) -> dict:
        return {"status": "generated", "prompt": prompt, "artifact": "app/index.html"}
