# API routes mínimas
from fastapi import APIRouter, Query, HTTPException
from app.controllers.hello_controller import HelloController
from app.controllers.queue_controller import QueueController
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
    description="Obtiene la proxima factura en cola usando los parametros de consulta `limite` y `host`.",
    response_model=PrintQueueResponse,
)
async def queue_next(
    limite: int = Query(1, ge=1, le=100, description="Cantidad máxima de registros a pedir."),
    host: int = Query(..., description="Identificador del host que solicita la factura."),
) -> PrintQueueResponse:
    try:
        settings = get_settings()
        http_client = HttpxClient()
        service = QueueService(http_client, settings)
        return await QueueController.get_next(service, limite, host)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
