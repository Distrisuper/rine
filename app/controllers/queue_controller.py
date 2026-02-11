from app.services.queue_service import fetch_next_invoice
from app.models import PrintQueueResponse

class QueueController:
    @staticmethod
    async def next_invoice(limit: int, host: int) -> PrintQueueResponse:
        """Controlador para obtener el siguiente comprobante en la cola."""
        return await fetch_next_invoice(limit=limit, host=host)
