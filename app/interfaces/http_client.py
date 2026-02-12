from abc import ABC, abstractmethod
from typing import Any


class HttpClient(ABC):
    """Interfaz para cliente HTTP. Permite inyectar distintas implementaciones."""

    @abstractmethod
    async def get(self, url: str, params: dict[str, Any]) -> dict[str, Any]:
        """Realiza GET y retorna JSON."""
        pass
