from infrastructure.config import Settings
from domain.repositories.http_client import HttpClient
from domain.entities.models import PrintQueueResponse

class QueueService:
    """Servicio para obtener comprobantes de la cola de impresión."""

    def __init__(self, http_client: HttpClient, settings: Settings):
        self._http_client = http_client
        self._settings = settings

    async def get_next(self, limite: int, host: int) -> PrintQueueResponse:
        """Obtiene el siguiente comprobante en la cola desde el servicio remoto."""
        if not self._settings.invoice_base_url:
            raise ValueError("INVOICE_BASE_URL is not configured")

        base_url = self._settings.invoice_base_url.rstrip("/")
        url = f"{base_url}/invoices/fifo/table/gm/print-queue"
        params = {"limit": limite, "host": host}

        respuesta = await self._http_client.get(url, params)
        return PrintQueueResponse(**respuesta)
