# API routes mínimas
import base64
import logging
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import JSONResponse, Response

from app.adapters.cups_printer_discovery import CupsPrinterDiscovery
from app.adapters.httpx_client import HttpxClient
from app.config import get_settings
from app.controllers.hello_controller import HelloController
from app.controllers.printer_controller import PrinterController
from app.controllers.queue_controller import QueueController
from app.controllers.template_controller import TemplateController
from app.interfaces.printer_discovery import PrinterDiscovery
from app.models import PrintQueueResponse, TemplateTestItem
from app.services.extra_data_parser import DefaultExtraDataParser
from app.services.label_data_provider import InlineLabelDataProvider
from app.services.label_render_service import PlaceholderLabelRenderer
from app.services.label_template_resolver import LegacyLabelTemplateResolver
from app.services.label_template_service import LabelTemplateService
from app.services.print_job_service import print_pdf_to_printer
from app.services.queue_service import QueueService
from app.services.remito_data_provider import InlineRemitoDataProvider
from app.services.remito_render_service import PlaceholderRemitoRenderer
from app.services.remito_template_resolver import LegacyRemitoTemplateResolver
from app.services.remito_template_service import RemitoTemplateService

logger = logging.getLogger(__name__)
router = APIRouter()


def get_printer_discovery() -> PrinterDiscovery:
    """Dependencia: implementación por defecto (CUPS o mock)."""
    return CupsPrinterDiscovery()


def get_remito_template_service() -> RemitoTemplateService:
    """Servicio de remito: HTML+WeasyPrint si está disponible, sino placeholder PDF."""
    try:
        from app.services.html_remito_render_service import HtmlRemitoRenderer
        renderer = HtmlRemitoRenderer()
    except Exception as e:
        logger.warning(
            "Remito HTML renderer no disponible, usando placeholder PDF: %s",
            e,
            exc_info=True,
        )
        renderer = PlaceholderRemitoRenderer()
    return RemitoTemplateService(
        parser=DefaultExtraDataParser(),
        resolver=LegacyRemitoTemplateResolver(),
        data_provider=InlineRemitoDataProvider(),
        renderer=renderer,
    )


def get_label_template_service() -> LabelTemplateService:
    """Dependencia: servicio de templates de etiqueta con implementaciones por defecto."""
    return LabelTemplateService(
        parser=DefaultExtraDataParser(),
        resolver=LegacyLabelTemplateResolver(),
        data_provider=InlineLabelDataProvider(),
        renderer=PlaceholderLabelRenderer(),
    )


@router.get("/", tags=["Health"])
async def root():
    return HelloController.root()


@router.get("/health", tags=["Health"])
async def health():
    return HelloController.health()


@router.get(
    "/queue/next",
    tags=["Queue"],
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


@router.get(
    "/printers/status",
    tags=["Printers"],
    summary="Estado de la flota de impresoras",
    description="Lista todas las impresoras detectadas por CUPS con ready/not_ready y detalles. En Windows devuelve _cups_unavailable.",
)
async def printers_status(discovery: PrinterDiscovery = Depends(get_printer_discovery)):
    return PrinterController.get_status(discovery)


@router.get(
    "/printers/status/{name}",
    tags=["Printers"],
    summary="Estado de una impresora",
    description="Estado de la impresora por nombre. 404 si no existe o CUPS no disponible.",
)
async def printer_status(name: str, discovery: PrinterDiscovery = Depends(get_printer_discovery)):
    data = PrinterController.get_printer_status(discovery, name)
    if data is None:
        raise HTTPException(status_code=404, detail="Impresora no encontrada o CUPS no disponible")
    return data


@router.post(
    "/templates/remito/test",
    tags=["Templates"],
    summary="Probar template remito (PDF)",
    description="Genera un PDF de remito con datos mock. Body: channel (4 u 8), location, opcional extra_data, server, ds. Si format=json devuelve JSON con content_base64 para inspeccionar.",
    response_class=Response,
)
async def template_remito_test(
    body: TemplateTestItem,
    service: RemitoTemplateService = Depends(get_remito_template_service),
    format: str = Query("binary", description="binary (PDF) o json (base64 para debug)"),
):
    try:
        response = TemplateController.render_remito_test(service, body)
        if format == "json":
            return JSONResponse(content={
                "content_type": "application/pdf",
                "size": len(response.body),
                "content_base64": base64.b64encode(response.body).decode("ascii"),
            })
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Error generando PDF remito: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/printers/{printer_name}/print/remito",
    tags=["Printers"],
    summary="Imprimir remito en una impresora (CUPS)",
    description="Genera el PDF del remito con el body indicado y envía el trabajo a la impresora por nombre. Solo funciona en Linux con CUPS; la impresora debe existir en CUPS (ej. PC42t). En Windows responde 503.",
)
async def print_remito_to_printer(
    printer_name: str,
    body: TemplateTestItem,
    service: RemitoTemplateService = Depends(get_remito_template_service),
):
    """Envía el remito (template + datos del body) a la impresora indicada."""
    try:
        item = body.to_queue_item()
        pdf_bytes = service.render(item)
        job_id = print_pdf_to_printer(printer_name, pdf_bytes, job_title="Remito")
        return {"printer": printer_name, "job_id": job_id}
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/templates/label/test",
    tags=["Templates"],
    summary="Probar template etiqueta (ZPL)",
    description="Genera ZPL de etiqueta con datos mock. Body: channel=3, location, opcional extra_data. Si format=json devuelve JSON con content_base64 para inspeccionar.",
    response_class=Response,
)
async def template_label_test(
    body: TemplateTestItem,
    service: LabelTemplateService = Depends(get_label_template_service),
    format: str = Query("binary", description="binary (ZPL) o json (base64 para debug)"),
):
    try:
        response = TemplateController.render_label_test(service, body)
        if format == "json":
            return JSONResponse(content={
                "content_type": "application/vnd.zpl",
                "size": len(response.body),
                "content_base64": base64.b64encode(response.body).decode("ascii"),
                "content_preview": response.body.decode("utf-8", errors="replace")[:500],
            })
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
