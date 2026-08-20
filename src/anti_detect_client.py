import httpx
from typing import Dict, Any

class AntiDetectClient:
    """
    Minimal async client for anti-detect Local REST API.
    Adapt to your specific anti-detect product (Dolphin/ADS Power) APIs.
    """
    def __init__(self, base_url: str, timeout: int = 10):
        self.base_url = base_url.rstrip('/')
        self.client = httpx.AsyncClient(timeout=timeout)

    async def create_profile(self, profile_spec: Dict[str, Any]) -> Dict[str, Any]:
        resp = await self.client.post(f"{self.base_url}/profiles", json=profile_spec)
        resp.raise_for_status()
        return resp.json()

    async def start_profile(self, profile_id: str) -> Dict[str, Any]:
        resp = await self.client.post(f"{self.base_url}/profiles/{profile_id}/start")
        resp.raise_for_status()
        return resp.json()

    async def stop_profile(self, profile_id: str) -> Dict[str, Any]:
        resp = await self.client.post(f"{self.base_url}/profiles/{profile_id}/stop")
        resp.raise_for_status()
        return resp.json()
