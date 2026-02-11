# API routes mínimas
from fastapi import APIRouter, Query
from app.controllers.hello_controller import HelloController
from app.controllers.queue_controller import QueueController

router = APIRouter()

@router.get("/", summary="Estado del servicio", description="Confirma que la API esta activa.")
async def root():
    return HelloController.root()

@router.get("/health", summary="Salud", description="Chequeo rapido de salud del servicio.")
async def health():
    return HelloController.health()

@router.get(
    "/queue/next",
    summary="Siguiente factura",
    description="Obtiene la proxima factura en cola usando los parametros de consulta `limit` y `host`.",
)
async def queue_next(
    limit: int = Query(1, ge=1, le=100, description="Cantidad maxima de registros a pedir."),
    host: int = Query(..., description="Identificador del host que solicita la factura."),
):
    return await QueueController.next_invoice(limit=limit, host=host)
