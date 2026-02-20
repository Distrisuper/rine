from app.interfaces.queue_repository import QueueRepository
from app.models import PrintQueueResponse

class QueueService:
    """Servicio para obtener comprobantes de la cola de impresión."""

    def __init__(self, repository: QueueRepository):
        self._repository = repository

    async def get_next(self, limit: int, host: int) -> PrintQueueResponse:
        """Obtiene el siguiente comprobante en la cola local."""
        if limit <= 0:
            raise ValueError("limit debe ser mayor a 0")

        data = await self._repository.dequeue_next(limit, host)
        return PrintQueueResponse(ok=1, data=data)
