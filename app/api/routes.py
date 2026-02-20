# API routes mínimas
from fastapi import APIRouter, Depends, Query, HTTPException
from app.controllers.hello_controller import HelloController
from app.controllers.queue_controller import QueueController
from app.controllers.print_controller import PrintController
from app.controllers.printer_controller import PrinterController
from app.models import PrintQueueResponse, PrintRequest, PrintResponse
from app.services.queue_service import QueueService
from app.services.print_service import PrintService
from app.adapters.httpx_client import HttpxClient
from app.adapters.cups_printer_discovery import CupsPrinterDiscovery
from app.interfaces.printer_discovery import PrinterDiscovery
from app.config import get_settings

router = APIRouter()


def get_printer_discovery() -> PrinterDiscovery:
    """Dependencia: implementación por defecto (CUPS o mock)."""
    return CupsPrinterDiscovery()

@router.get("/")
async def root():
    return HelloController.root()

@router.get("/health")
async def health():
    return HelloController.health()

@router.get(
    "/queue/next",
    summary="Siguiente factura",
    description="Obtiene la proxima factura en cola usando los parametros de consulta `limit` y `host`.",
    response_model=PrintQueueResponse,
)
async def queue_next(
    limit: int = Query(1, ge=1, le=100, description="Cantidad máxima de registros a pedir."),
    host: int = Query(..., description="Identificador del host que solicita la factura."),
) -> PrintQueueResponse:
    try:
        settings = get_settings()
        http_client = HttpxClient()
        service = QueueService(http_client, settings)
        return await QueueController.get_next(service, limit, host)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/print",
    response_model=PrintResponse,
    summary="Imprime comprobante",
    description="""
Endpoint unificado para imprimir diferentes tipos de comprobantes.

## Tipos disponibles:

### 🏷️ ETIQ (Etiqueta de envío)
Campos requeridos adicionales:
- `client_address`
- `client_city` 
- `package_quantity`
- `label_packages`

### 📄 REMI (Remito de entrega)
Campos requeridos adicionales:
- `client_address`
- `client_city`
- `location`
- `remitos_quantity`
- `label_packages`

### 📋 GM (Pedido de impresión)
Campos requeridos adicionales:
- `location`
- `invoices_quantity`

### ⏳ PEND (Redi pendiente)
Campos requeridos adicionales:
- `location`
- `package_quantity`
- `pending`

---

**Campos base siempre requeridos:** `type`, `client_code`, `client_name`, `set_host`, `redi_code`, `id_remito`
""",
    responses={
        200: {
            "description": "Impresión procesada exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "ok": 1,
                        "message": "Imprimiendo etiqueta para cliente CL001 (Distribuidora ABC)...",
                        "doc_type": "etiqueta"
                    }
                }
            }
        },
        400: {
            "description": "Error de validación: tipo inválido o campos requeridos faltantes",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_type": {
                            "summary": "Tipo inválido",
                            "value": {"detail": "Tipo de impresión inválido: INVALID"}
                        },
                        "missing_fields": {
                            "summary": "Campos faltantes",
                            "value": {"detail": "ETIQ requiere: client_address, client_city, package_quantity, label_packages"}
                        }
                    }
                }
            }
        }
    }
)
async def print_document(request: PrintRequest) -> PrintResponse:
    """Procesa impresión según tipo de comprobante."""
    try:
        service = PrintService()
        return await PrintController.process_print(service, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- Monitoreo de impresoras (CUPS) - testing por interfaz ---
@router.get(
    "/printers/status",
    summary="Estado de la flota de impresoras",
    description="Lista todas las impresoras detectadas por CUPS con ready/not_ready y detalles. En Windows devuelve _cups_unavailable.",
)
async def printers_status(discovery: PrinterDiscovery = Depends(get_printer_discovery)):
    return PrinterController.get_status(discovery)


@router.get(
    "/printers/status/{name}",
    summary="Estado de una impresora",
    description="Estado de la impresora por nombre. 404 si no existe o CUPS no disponible.",
)
async def printer_status(name: str, discovery: PrinterDiscovery = Depends(get_printer_discovery)):
    data = PrinterController.get_printer_status(discovery, name)
    if data is None:
        raise HTTPException(status_code=404, detail="Impresora no encontrada o CUPS no disponible")
    return data
