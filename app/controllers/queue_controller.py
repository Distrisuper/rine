from app.services.queue_service import QueueService
from app.models import PrintQueueResponse


class QueueController:
    """Controlador para operaciones de cola de impresión."""

    @staticmethod
    async def get_next(service: QueueService, limit: int, host: int) -> PrintQueueResponse:
        """Obtiene el siguiente comprobante en la cola."""
        return await service.get_next(limit, host)
