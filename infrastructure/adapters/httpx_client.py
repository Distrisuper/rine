from typing import Any

import httpx

from domain.repositories.http_client import HttpClient


class HttpxClient(HttpClient):
    """Adaptador de httpx que implementa la interfaz HttpClient."""

    async def get(self, url: str, params: dict[str, Any]) -> dict[str, Any]:
        """Realiza GET con httpx y retorna JSON."""
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
