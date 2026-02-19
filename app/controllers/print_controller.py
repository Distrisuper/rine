from app.services.print_service import PrintService
from app.models import PrintRequest, PrintResponse


class PrintController:
    """Controlador para operaciones de impresión."""

    @staticmethod
    async def process_print(service: PrintService, request: PrintRequest) -> PrintResponse:
        """Procesa solicitud de impresión."""
        return await service.process_print(request)
