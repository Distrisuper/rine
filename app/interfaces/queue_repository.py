from abc import ABC, abstractmethod
from typing import Iterable

from app.models import QueueItem


class QueueRepository(ABC):
    """Interfaz de persistencia para la cola de impresión."""

    @abstractmethod
    async def initialize(self) -> None:
        """Crea el esquema si no existe."""
        raise NotImplementedError

    @abstractmethod
    async def enqueue_items(self, items: Iterable[QueueItem]) -> None:
        """Agrega items a la cola local."""
        raise NotImplementedError

    @abstractmethod
    async def dequeue_next(self, limit: int, host: int) -> list[QueueItem]:
        """Obtiene y marca como en proceso los siguientes items."""
        raise NotImplementedError
