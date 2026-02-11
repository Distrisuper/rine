# API routes mínimas
from fastapi import APIRouter, Query, HTTPException
from app.controllers.hello_controller import HelloController
from app.controllers.queue_controller import QueueController

router = APIRouter()

@router.get("/")
async def root():
    return HelloController.root()

@router.get("/health")
async def health():
    return HelloController.health()

from app.models import PrintQueueResponse


@router.get(
    "/queue/next",
    summary="Siguiente factura",
    description="Obtiene la proxima factura en cola usando los parametros de consulta `limit` y `host`.",
    response_model=PrintQueueResponse,
)
async def queue_next(
    limit: int = Query(1, ge=1, le=100, description="Cantidad maxima de registros a pedir."),
    host: int = Query(..., description="Identificador del host que solicita la factura."),
) -> PrintQueueResponse:
    try:
        return await QueueController.next_invoice(limit=limit, host=host)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
