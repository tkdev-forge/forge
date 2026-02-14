from dataclasses import dataclass


@dataclass
class RLIRequest:
    member: str
    task_id: str
    task_category: str
    deliverable_ipfs_hash: str


class RLIOracleClient:
    def request_evaluation(self, payload: RLIRequest) -> dict:
        return {
            "status": "queued",
            "member": payload.member,
            "task_id": payload.task_id,
            "task_category": payload.task_category,
        }
