# API routes mínimas
from fastapi import APIRouter, Query, HTTPException
from app.controllers.hello_controller import HelloController
from app.controllers.queue_controller import QueueController
from app.controllers.printer_controller import PrinterController
from app.models import PrintQueueResponse
from app.services.queue_service import QueueService
from app.adapters.httpx_client import HttpxClient
from app.config import get_settings

router = APIRouter()

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


# --- Monitoreo de impresoras (CUPS) - testing por interfaz ---
@router.get(
    "/printers/status",
    summary="Estado de la flota de impresoras",
    description="Lista todas las impresoras detectadas por CUPS con ready/not_ready y detalles. En Windows devuelve _cups_unavailable.",
)
async def printers_status():
    return PrinterController.get_status()


@router.get(
    "/printers/status/{name:path}",
    summary="Estado de una impresora",
    description="Estado de la impresora por nombre. 404 si no existe o CUPS no disponible.",
)
async def printer_status(name: str):
    data = PrinterController.get_printer_status(name)
    if data is None:
        raise HTTPException(status_code=404, detail="Impresora no encontrada o CUPS no disponible")
    return data
