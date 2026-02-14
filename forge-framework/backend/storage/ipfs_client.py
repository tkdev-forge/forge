import os

import httpx


class IPFSStorage:
    def __init__(self):
        self.base_url = os.getenv("IPFS_API_URL", "http://ipfs:5001")
        self.timeout = float(os.getenv("IPFS_TIMEOUT_SEC", "10"))

    def upload(self, content: bytes) -> str:
        files = {"file": ("upload.bin", content)}
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(f"{self.base_url}/api/v0/add", files=files)
            resp.raise_for_status()
            data = resp.json()
            return data["Hash"]

    def download(self, cid: str) -> bytes:
        params = {"arg": cid}
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(f"{self.base_url}/api/v0/cat", params=params)
            resp.raise_for_status()
            return resp.content
