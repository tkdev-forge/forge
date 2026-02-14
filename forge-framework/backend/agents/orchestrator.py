class OrchestratorAgent:
    def __init__(self, max_steps: int = 10, max_budget_per_task: float = 100.0):
        self.max_steps = max_steps
        self.max_budget_per_task = max_budget_per_task

    def coordinate(self, task: dict) -> dict:
        return {"status": "coordinated", "task": task, "max_steps": self.max_steps}
