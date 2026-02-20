from abc import ABC, abstractmethod

from app.models import PrintJobRecord, PrintJobStatus, PrintRequest


class PrintJobRepository(ABC):
    """Interfaz de persistencia para trabajos de impresion."""

    @abstractmethod
    async def initialize(self) -> None:
        """Crea el esquema si no existe."""
        raise NotImplementedError

    @abstractmethod
    async def enqueue_job(
        self,
        request: PrintRequest,
        status: PrintJobStatus,
        created_at: str,
        print_count: int,
        payload: str,
    ) -> PrintJobRecord:
        """Encola un trabajo de impresión."""
        raise NotImplementedError
