# API routes mínimas
import base64
import logging
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import JSONResponse, Response

from infrastructure.config import get_settings
from infrastructure.controllers.hello.hello_get_controller import HelloGetController
from infrastructure.controllers.hello.health_controller import HealthController
from infrastructure.controllers.template.render_remito_controller import RenderRemitoController
from infrastructure.controllers.template.render_label_controller import RenderLabelController
from domain.services.printer_discovery import PrinterDiscovery
from domain.entities.models import TemplateTestItem
from infrastructure.services.extra_data_parser import DefaultExtraDataParser
from domain.services.label_data_provider import InlineLabelDataProvider
from domain.services.label_render_service import PlaceholderLabelRenderer
from domain.services.label_template_resolver import LegacyLabelTemplateResolver
from domain.services.label_template_service import LabelTemplateService
from infrastructure.print_job_service import print_pdf_to_printer
from domain.services.remito_data_provider import InlineRemitoDataProvider
from domain.services.remito_render_service import PlaceholderRemitoRenderer
from domain.services.remito_template_resolver import LegacyRemitoTemplateResolver
from domain.services.remito_template_service import RemitoTemplateService
from application.use_cases.hello.get.get_hello_use_case_interface import GetHelloUseCaseInterface
from application.use_cases.hello.get.get_hello_use_case import GetHelloUseCase
from application.use_cases.hello.health.health_use_case_interface import HealthUseCaseInterface
from application.use_cases.hello.health.health_use_case import HealthUseCase
from application.use_cases.printer.get_status.get_status_use_case_interface import GetStatusUseCaseInterface
from application.use_cases.printer.get_status.get_status_use_case import GetStatusUseCase
from infrastructure.controllers.printer.get_status_controller import GetStatusController
from application.use_cases.printer.get_one_status_by_name.get_one_status_by_name_use_case_interface import GetOneStatusByNameUseCaseInterface
from application.use_cases.printer.get_one_status_by_name.get_one_status_by_name_use_case import GetOneStatusByNameUseCase
from application.use_cases.printer.discover.discover_printer_use_case_interface import DiscoverPrinterUseCaseInterface
from application.use_cases.printer.discover.discover_printer_use_case import DiscoverPrinterUseCase
from infrastructure.controllers.printer.get_one_status_by_name_controller import GetOneStatusByNameController
from application.use_cases.template.render_remito.render_remito_use_case_interface import RenderRemitoUseCaseInterface
from application.use_cases.template.render_remito.render_remito_use_case import RenderRemitoUseCase
from application.use_cases.template.render_label.render_label_use_case_interface import RenderLabelUseCaseInterface
from application.use_cases.template.render_label.render_label_use_case import RenderLabelUseCase
from application.use_cases.print_jobs.create.create_print_job_use_case import CreatePrintJobUseCase
from application.use_cases.print_jobs.create.create_print_job_use_case_interface import CreatePrintJobUseCaseInterface
from infrastructure.controllers.print_jobs.create.create_print_job_controller import CreatePrintJobController
from domain.repositories.printer_repository import PrinterRepository
from domain.repositories.channel_repository import ChannelRepository
from pydantic import BaseModel
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)
router = APIRouter()

logger = logging.getLogger(__name__)


def get_hello_controller() -> HelloGetController:
    use_case = GetHelloUseCase()
    return HelloGetController(use_case)


def get_health_controller() -> HealthController:
    use_case = HealthUseCase()
    return HealthController(use_case)


def get_printer_discovery() -> PrinterDiscovery:
    """Dependencia: implementación por defecto (CUPS o mock)."""
    from infrastructure.services.printer_discovery_service import CupsPrinterDiscoveryService
    return CupsPrinterDiscoveryService()


def get_status_controller() -> GetStatusController:
    discovery = get_printer_discovery()
    use_case = GetStatusUseCase(discovery)
    return GetStatusController(use_case)


def get_one_status_by_name_controller() -> GetOneStatusByNameController:
    discovery = get_printer_discovery()
    use_case = GetOneStatusByNameUseCase(discovery)
    return GetOneStatusByNameController(use_case)


def get_printer_repository() -> PrinterRepository:
    from infrastructure.db.database import engine
    return PrinterRepository(engine)


def get_channel_repository() -> ChannelRepository:
    from infrastructure.db.database import engine
    return ChannelRepository(engine)


# Pydantic models for channels
class ChannelCreate(BaseModel):
    channel_number: int
    description: Optional[str] = None


class ChannelUpdate(BaseModel):
    description: Optional[str] = None
    is_active: Optional[bool] = None


class PrinterCreate(BaseModel):
    name: str
    channel_ids: List[int] = []


class PrinterUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None
    channel_ids: Optional[List[int]] = None


class PrinterChannelsUpdate(BaseModel):
    channel_ids: List[int]


def get_remito_template_service() -> RemitoTemplateService:
    """Servicio de remito: HTML+WeasyPrint si está disponible, sino placeholder PDF."""
    from infrastructure.services.barcode_service import BarcodeService
    barcode_service = BarcodeService()
    try:
        from infrastructure.html_remito_render_service import HtmlRemitoRenderer
        renderer = HtmlRemitoRenderer(barcode_service)
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


def get_render_remito_controller() -> RenderRemitoController:
    template_service = get_remito_template_service()
    use_case = RenderRemitoUseCase(template_service)
    return RenderRemitoController(use_case)


def get_render_label_controller() -> RenderLabelController:
    template_service = get_label_template_service()
    use_case = RenderLabelUseCase(template_service)
    return RenderLabelController(use_case)


class CreatePrintJobRequest(BaseModel):
    channel: int
    client_code: str
    client_name: str
    payload: Dict[str, Any]


def get_create_print_job_controller() -> CreatePrintJobController:
    use_case = CreatePrintJobUseCase()
    return CreatePrintJobController(use_case)


@router.get("/", tags=["Health"])
async def root(controller: HelloGetController = Depends(get_hello_controller)):
    return controller()


@router.get("/health", tags=["Health"])
async def health(controller: HealthController = Depends(get_health_controller)):
    return controller()


@router.get(
    "/printers/status",
    tags=["Printers"],
    summary="Estado de la flota de impresoras",
    description="Lista todas las impresoras detectadas por CUPS con ready/not_ready y detalles. En Windows devuelve _cups_unavailable.",
)
async def printers_status(controller: GetStatusController = Depends(get_status_controller)):
    return controller()


@router.get(
    "/printers/status/{name}",
    tags=["Printers"],
    summary="Estado de una impresora",
    description="Estado de la impresora por nombre. 404 si no existe o CUPS no disponible.",
)
async def printer_status(name: str, controller: GetOneStatusByNameController = Depends(get_one_status_by_name_controller)):
    data = controller(name)
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
    controller: RenderRemitoController = Depends(get_render_remito_controller),
    format: str = Query("binary", description="binary (PDF) o json (base64 para debug)"),
):
    try:
        response = controller(body)
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
    controller: RenderLabelController = Depends(get_render_label_controller),
    format: str = Query("binary", description="binary (ZPL) o json (base64 para debug)"),
):
    try:
        response = controller(body)
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


@router.post(
    "/print-jobs",
    tags=["PrintJobs"],
    summary="Crear trabajo de impresión",
    description="Crea un nuevo trabajo de impresión pendiente. El worker lo procesará.",
)
async def create_print_job(
    body: CreatePrintJobRequest,
    controller: CreatePrintJobController = Depends(get_create_print_job_controller),
):
    try:
        return controller(
            channel=body.channel,
            client_code=body.client_code,
            client_name=body.client_name,
            payload=body.payload,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/printers/discover",
    tags=["Printers"],
    summary="Descubrir impresoras",
    description="Usa CUPS para descubrir impresoras disponibles en el sistema.",
)
async def discover_printers(
    discovery: PrinterDiscovery = Depends(get_printer_discovery),
):
    """Usa PrinterDiscovery para encontrar impresoras."""
    use_case = DiscoverPrinterUseCase(discovery)
    return use_case()


@router.get(
    "/printers",
    tags=["Printers"],
    summary="Listar impresoras configuradas",
    description="Lista todas las impresoras con sus channels.",
)
async def list_printers(repo: PrinterRepository = Depends(get_printer_repository)):
    return repo.get_all_printers_with_channels()


@router.post(
    "/printers",
    tags=["Printers"],
    summary="Crear impresora",
    description="Crea una nueva impresora con channels asociados.",
)
async def create_printer(
    body: PrinterCreate,
    repo: PrinterRepository = Depends(get_printer_repository),
):
    return repo.create_printer(body.name, body.channel_ids or [])


@router.put(
    "/printers/{printer_id}",
    tags=["Printers"],
    summary="Editar impresora",
    description="Edita una impresora y sus channels.",
)
async def update_printer(
    printer_id: int,
    body: PrinterUpdate,
    repo: PrinterRepository = Depends(get_printer_repository),
):
    printer = repo.update_printer(
        printer_id,
        name=body.name,
        is_active=body.is_active,
    )
    if not printer:
        raise HTTPException(status_code=404, detail="Impresora no encontrada")
    
    if body.channel_ids is not None:
        repo.set_printer_channels(printer_id, body.channel_ids)
        printer["channels"] = repo.get_printer_channels(printer_id)
    
    return printer


@router.delete(
    "/printers/{printer_id}",
    tags=["Printers"],
    summary="Eliminar impresora",
    description="Elimina una impresora y sus channels asociados.",
)
async def delete_printer(
    printer_id: int,
    repo: PrinterRepository = Depends(get_printer_repository),
):
    success = repo.delete_printer(printer_id)
    if not success:
        raise HTTPException(status_code=404, detail="Impresora no encontrada")
    return {"status": "deleted"}


# Channels endpoints
@router.get(
    "/channels",
    tags=["Channels"],
    summary="Listar channels",
    description="Lista todos los channels configurados.",
)
async def list_channels(repo: ChannelRepository = Depends(get_channel_repository)):
    channels = repo.get_all()
    return [
        {
            "id": c.id,
            "channel_number": c.channel_number,
            "description": c.description,
            "is_active": c.is_active,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        }
        for c in channels
    ]


@router.post(
    "/channels",
    tags=["Channels"],
    summary="Crear channel",
    description="Crea un nuevo channel.",
)
async def create_channel(
    body: ChannelCreate,
    repo: ChannelRepository = Depends(get_channel_repository),
):
    existing = repo.get_by_number(body.channel_number)
    if existing:
        raise HTTPException(status_code=400, detail=f"Channel {body.channel_number} ya existe")
    
    channel = repo.create(body.channel_number, body.description)
    return {
        "id": channel.id,
        "channel_number": channel.channel_number,
        "description": channel.description,
        "is_active": channel.is_active,
    }


@router.put(
    "/channels/{channel_id}",
    tags=["Channels"],
    summary="Editar channel",
    description="Edita la descripción o estado de un channel.",
)
async def update_channel(
    channel_id: int,
    body: ChannelUpdate,
    repo: ChannelRepository = Depends(get_channel_repository),
):
    channel = repo.update(channel_id, body.description, body.is_active)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel no encontrado")
    return {
        "id": channel.id,
        "channel_number": channel.channel_number,
        "description": channel.description,
        "is_active": channel.is_active,
    }


@router.delete(
    "/channels/{channel_id}",
    tags=["Channels"],
    summary="Eliminar channel",
    description="Elimina un channel.",
)
async def delete_channel(
    channel_id: int,
    repo: ChannelRepository = Depends(get_channel_repository),
):
    success = repo.delete(channel_id)
    if not success:
        raise HTTPException(status_code=404, detail="Channel no encontrado")
    return {"status": "deleted"}
