# API routes mínimas
import base64
import json
import logging
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import JSONResponse, Response

from infrastructure.config import get_settings
from infrastructure.controllers.hello.hello_get_controller import HelloGetController
from infrastructure.controllers.health.health_controller import HealthController
from infrastructure.controllers.template.render_remito_controller import RenderRemitoController
from infrastructure.controllers.template.label_preview.label_preview_controller import LabelPreviewController
from domain.services.printer_discovery import PrinterDiscovery
from domain.entities.models import TemplateTestItem
from infrastructure.services.extra_data_parser import DefaultExtraDataParser
from domain.services.label_data_provider import InlineLabelDataProvider
from domain.services.label_render_service import PlaceholderLabelRenderer
from domain.services.label_template_resolver import LegacyLabelTemplateResolver
from domain.services.label_template_service import LabelTemplateService
from infrastructure.print_job_service import print_pdf_to_printer, print_raw_to_printer
from domain.services.remito_data_provider import InlineRemitoDataProvider
from domain.services.remito_render_service import PlaceholderRemitoRenderer
from domain.services.remito_template_resolver import LegacyRemitoTemplateResolver
from domain.services.remito_template_service import RemitoTemplateService
from application.use_cases.hello.get.get_hello_use_case_interface import GetHelloUseCaseInterface
from application.use_cases.hello.get.get_hello_use_case import GetHelloUseCase
from application.use_cases.health.health_use_case_interface import HealthUseCaseInterface
from application.use_cases.health.health_use_case import HealthUseCase
from application.use_cases.printer.get_status.get_status_use_case_interface import GetStatusUseCaseInterface
from application.use_cases.printer.get_status.get_status_use_case import GetStatusUseCase
from infrastructure.controllers.printer.get_status.get_status_controller import GetStatusController
from application.use_cases.printer.get_one_status_by_name.get_one_status_by_name_use_case_interface import GetOneStatusByNameUseCaseInterface
from application.use_cases.printer.get_one_status_by_name.get_one_status_by_name_use_case import GetOneStatusByNameUseCase
from application.use_cases.printer.discover.discover_printer_use_case_interface import DiscoverPrinterUseCaseInterface
from application.use_cases.printer.discover.discover_printer_use_case import DiscoverPrinterUseCase
from infrastructure.controllers.printer.get_one_status_by_name.get_one_status_by_name_controller import GetOneStatusByNameController
from application.use_cases.template.render_remito.render_remito_use_case_interface import RenderRemitoUseCaseInterface
from application.use_cases.template.render_remito.render_remito_use_case import RenderRemitoUseCase
from application.use_cases.template.render_label.render_label_use_case_interface import RenderLabelUseCaseInterface
from application.use_cases.template.render_label.render_label_use_case import RenderLabelUseCase
from application.use_cases.print_jobs.create.create_print_job_use_case import CreatePrintJobUseCase
from application.use_cases.print_jobs.create.create_print_job_use_case_interface import CreatePrintJobUseCaseInterface
from infrastructure.controllers.print_jobs.create.create_print_job_controller import CreatePrintJobController
from domain.repositories.printer_repository import PrinterRepository
from domain.repositories.channel_repository import ChannelRepository

# DTOs
from infrastructure.dtos.channels.create.request import CreateChannelRequestDTO
from infrastructure.dtos.channels.create.response import CreateChannelResponseDTO
from infrastructure.dtos.channels.update.request import UpdateChannelRequestDTO
from infrastructure.dtos.printers.create.request import CreatePrinterRequestDTO
from infrastructure.dtos.printers.update.request import UpdatePrinterRequestDTO
from infrastructure.dtos.print_jobs.create.request import CreatePrintJobRequestDTO
from infrastructure.dtos.print_jobs.create.response import CreatePrintJobResponseDTO
from infrastructure.dtos.print_jobs.print.request import PrintJobRequestDTO
from infrastructure.dtos.print_jobs.print.response import PrintJobResponseDTO
from infrastructure.dtos.printer.discover.response import DiscoverPrinterResponseDTO
from infrastructure.dtos.printer.get_one_status_by_name.request import GetOneStatusByNameRequestDTO
from infrastructure.dtos.printer.get_one_status_by_name.response import GetOneStatusByNameResponseDTO
from infrastructure.dtos.printer.get_status.response import GetStatusResponseDTO
from infrastructure.dtos.template.label_preview.request import LabelPreviewRequestDTO

# Use Cases
from application.use_cases.channels.create.create_channel_use_case import CreateChannelUseCase
from application.use_cases.channels.create.create_channel_use_case_interface import CreateChannelUseCaseInterface

# Controllers
from infrastructure.controllers.channels.create.create_channel_controller import CreateChannelController
from infrastructure.controllers.printer.discover.discover_printer_controller import DiscoverPrinterController
from infrastructure.api.container import container
from domain.repositories.template_repository import TemplateRepository
from pydantic import BaseModel
from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlmodel import select, and_, desc

logger = logging.getLogger(__name__)
router = APIRouter()

logger = logging.getLogger(__name__)


def get_printer_discovery() -> PrinterDiscovery:
    """Dependencia: implementación por defecto (CUPS o mock)."""
    from infrastructure.services.printer_discovery_service import CupsPrinterDiscoveryService
    return CupsPrinterDiscoveryService()


def get_printer_repository() -> PrinterRepository:
    from infrastructure.db.database import engine
    return PrinterRepository(engine)


def get_channel_repository() -> ChannelRepository:
    from infrastructure.db.database import engine
    return ChannelRepository(engine)


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


class CreatePrintJobRequest(BaseModel):
    channel: int
    client_code: str
    client_name: str
    payload: Dict[str, Any]


@router.get("/", tags=["Health"])
async def root(controller: HelloGetController = Depends(container.hello_controller)):
    return controller()


@router.get("/health", tags=["Health"])
async def health(controller: HealthController = Depends(container.health_controller)):
    return controller()


@router.get(
    "/printers/status",
    tags=["Printers"],
    summary="Estado de la flota de impresoras",
    description="Lista todas las impresoras detectadas por CUPS con ready/not_ready y detalles. En Windows devuelve _cups_unavailable.",
    response_model=GetStatusResponseDTO,
)
async def printers_status(controller: GetStatusController = Depends(container.get_status_controller)):
    return controller()


@router.get(
    "/printers/status/{name}",
    tags=["Printers"],
    summary="Estado de una impresora",
    description="Estado de la impresora por nombre. 404 si no existe o CUPS no disponible.",
    response_model=GetOneStatusByNameResponseDTO,
)
async def printer_status(
    name: str,
    controller: GetOneStatusByNameController = Depends(container.get_one_status_by_name_controller),
):
    return controller(name)


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
    "/printers/{printer_name}/print/label",
    tags=["Printers"],
    summary="Imprimir etiqueta (ZPL) en una impresora (CUPS)",
    description="Genera el ZPL de la etiqueta con el body indicado (channel=3) y envía el trabajo a la impresora por nombre. Para Zebra/etiquetas la cola en CUPS debe ser raw (-m raw). Solo Linux con CUPS; en Windows responde 503.",
)
async def print_label_to_printer(
    printer_name: str,
    body: TemplateTestItem,
    service: LabelTemplateService = Depends(get_label_template_service),
):
    """Envía la etiqueta (template + datos del body) a la impresora indicada como ZPL raw."""
    try:
        item = body.to_queue_item()
        zpl_bytes = service.render(item)
        job_id = print_raw_to_printer(printer_name, zpl_bytes, job_title="Etiqueta", suffix=".zpl")
        return {"printer": printer_name, "job_id": job_id}
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/templates/label/preview",
    tags=["Templates"],
    summary="Preview template etiqueta (ZPL)",
    description="Genera ZPL de etiqueta para preview.",
    response_class=Response,
)
async def label_preview(
    body: LabelPreviewRequestDTO,
    format: str = Query("binary", description="binary (ZPL) o json (base64)"),
    controller: LabelPreviewController = Depends(container.label_preview_controller),
):
    return controller(body, format=format)


@router.post(
    "/print-jobs",
    tags=["PrintJobs"],
    summary="Crear trabajo de impresión",
    description="Crea un nuevo trabajo de impresión pendiente. El worker lo procesará.",
    response_model=CreatePrintJobResponseDTO,
)
async def create_print_job(
    body: CreatePrintJobRequestDTO,
    controller: CreatePrintJobController = Depends(container.create_print_job_controller),
):
    return controller(
        channel=body.channel,
        client_code=body.client_code,
        client_name=body.client_name,
        payload=body.payload,
    )


class PrintJobResponse(BaseModel):
    id: int
    client_code: str
    client_name: str
    channel: int
    status: str
    print_count: int
    print_type: Optional[str]
    date_created: datetime
    date_started: Optional[datetime]
    date_processed: Optional[datetime]
    printer_name: Optional[str]
    error_message: Optional[str]


@router.get(
    "/print-jobs",
    tags=["PrintJobs"],
    summary="Listar trabajos de impresión",
    description="Lista trabajos de impresión con filtros opcionales.",
)
async def list_print_jobs(
    printer_name: Optional[str] = Query(None, description="Filtrar por nombre de impresora"),
    date_from: Optional[datetime] = Query(None, description="Fecha inicio (ISO)"),
    date_to: Optional[datetime] = Query(None, description="Fecha fin (ISO)"),
    status: Optional[str] = Query(None, description="Filtrar por status: pending, printed, failed"),
    page: int = Query(1, ge=1, description="Página"),
    limit: int = Query(100, ge=1, le=500, description="Registros por página"),
):
    from domain.entities.print_job import PrintJob
    from infrastructure.db.database import engine
    from sqlmodel import Session

    with Session(engine) as session:
        query = select(PrintJob)

        filters = []
        if printer_name:
            filters.append(PrintJob.printer_name == printer_name)
        if date_from:
            filters.append(PrintJob.date_created >= date_from)
        if date_to:
            filters.append(PrintJob.date_created <= date_to)
        if status:
            filters.append(PrintJob.status == status)

        if filters:
            query = query.where(and_(*filters))

        query = query.order_by(desc(PrintJob.date_created))

        total = len(session.exec(query).all())
        query = query.offset((page - 1) * limit).limit(limit)
        jobs = session.exec(query).all()

        return {
            "data": [
                {
                    "id": j.id,
                    "client_code": j.client_code,
                    "client_name": j.client_name,
                    "channel": j.channel,
                    "status": j.status,
                    "print_count": j.print_count,
                    "print_type": j.print_type,
                    "date_created": j.date_created.isoformat() if j.date_created else None,
                    "date_started": j.date_started.isoformat() if j.date_started else None,
                    "date_processed": j.date_processed.isoformat() if j.date_processed else None,
                    "printer_name": j.printer_name,
                    "error_message": j.error_message,
                }
                for j in jobs
            ],
            "page": page,
            "limit": limit,
            "total": total,
        }


@router.get(
    "/printers/discover",
    tags=["Printers"],
    summary="Descubrir impresoras",
    description="Usa CUPS para descubrir impresoras disponibles en el sistema.",
    response_model=list[DiscoverPrinterResponseDTO],
)
async def discover_printers(
    controller: DiscoverPrinterController = Depends(container.discover_printer_controller),
):
    return controller()


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
    body: CreatePrinterRequestDTO,
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
    body: UpdatePrinterRequestDTO,
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


@router.post(
    "/printers/{printer_id}/test",
    tags=["Printers"],
    summary="Test de impresión",
    description="Envía trabajos de prueba a todos los channels configurados en la impresora.",
)
async def test_printer(
    printer_id: int,
    repo: PrinterRepository = Depends(get_printer_repository),
):
    from domain.entities.channel import Channel
    from domain.entities.template import Template
    from domain.entities.print_job import PrintJob
    from infrastructure.db.database import engine
    from sqlmodel import Session
    import random

    printer = repo.get_printer_by_id(printer_id)
    if not printer:
        raise HTTPException(status_code=404, detail="Impresora no encontrada")

    channels = repo.get_printer_channels(printer_id)
    if not channels:
        raise HTTPException(status_code=400, detail="La impresora no tiene channels configurados")

    created_jobs = []

    with Session(engine) as session:
        for ch in channels:
            channel_obj = session.get(Channel, ch["channel_id"])
            if not channel_obj or not channel_obj.template_id:
                continue

            template = session.get(Template, channel_obj.template_id)
            if not template:
                continue

            file_path = template.file_path.lower()
            if file_path.endswith(".zpl"):
                payload = {
                    "to": f"Test Destinatario {random.randint(1000, 9999)}",
                    "address": f"Test Dirección {random.randint(100, 999)}",
                    "city": "Test Ciudad",
                    "packages": f"{random.randint(1, 5)} bulto(s)",
                }
            elif file_path.endswith(".html"):
                payload = {
                    "client_code": f"{random.randint(100, 999)}",
                    "client_name": "Test Cliente S.A.",
                    "order_number": random.randint(1000, 9999),
                    "address": f"Test Dirección {random.randint(100, 999)}",
                    "city": "Test Ciudad",
                    "items": [
                        {"codigo": "TEST001", "cantidad": random.randint(1, 10), "descripcion": "Producto de prueba"},
                        {"codigo": "TEST002", "cantidad": random.randint(1, 5), "descripcion": "Otro producto"},
                    ],
                    "total": round(random.uniform(100, 5000), 2),
                    "remito_id": f"R-TEST-{random.randint(100000, 999999)}",
                    "fecha": "27/02/2026",
                    "reparto": "Test Reparto",
                    "sucursal": "001",
                    "obs": "Trabajo de prueba",
                    "cant_unidades": str(random.randint(1, 20)),
                    "valor_declarado": f"${random.randint(100, 5000)}",
                    "numero_cot": f"COT-{random.randint(10000, 99999)}",
                    "numero_cai": f"CAI-{random.randint(10000, 99999)}",
                    "vencimiento": "15/03/2026",
                    "disclaimer": "Trabajo de prueba generado desde admin",
                }
            else:
                continue

            job = PrintJob(
                client_code=payload.get("client_code", "TEST"),
                client_name=payload.get("client_name", "Test Cliente"),
                channel=ch["channel_number"],
                payload=json.dumps(payload),
                status="pending",
                print_count=0,
            )
            session.add(job)
            session.commit()
            session.refresh(job)

            created_jobs.append({
                "id": job.id,
                "channel": ch["channel_number"],
                "template": template.name,
                "status": job.status,
            })

    return {"printer": printer.name, "jobs": created_jobs}


# Channels endpoints
def get_template_repository():
    from infrastructure.db.database import engine
    from domain.repositories.template_repository import TemplateRepository
    return TemplateRepository(engine)


@router.get(
    "/channels",
    tags=["Channels"],
    summary="Listar channels",
    description="Lista todos los channels configurados.",
)
async def list_channels(
    repo: ChannelRepository = Depends(get_channel_repository),
    template_repo: TemplateRepository = Depends(get_template_repository),
):
    channels = repo.get_all()
    templates = {t.id: t.name for t in template_repo.get_all()}
    return [
        {
            "id": c.id,
            "channel_number": c.channel_number,
            "description": c.description,
            "template_id": c.template_id,
            "template_name": templates.get(c.template_id),
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
    response_model=CreateChannelResponseDTO,
)
async def create_channel(
    body: CreateChannelRequestDTO,
    controller: CreateChannelController = Depends(container.create_channel_controller),
):
    return controller(
        channel_number=body.channel_number,
        description=body.description,
        template_id=body.template_id,
    )


@router.put(
    "/channels/{channel_id}",
    tags=["Channels"],
    summary="Editar channel",
    description="Edita la descripción o estado de un channel.",
)
async def update_channel(
    channel_id: int,
    body: UpdateChannelRequestDTO,
    repo: ChannelRepository = Depends(get_channel_repository),
):
    channel = repo.update(channel_id, body.description, body.is_active, body.template_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel no encontrado")
    return {
        "id": channel.id,
        "channel_number": channel.channel_number,
        "description": channel.description,
        "is_active": channel.is_active,
        "template_id": channel.template_id,
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


# Templates endpoints
@router.get(
    "/templates",
    tags=["Templates"],
    summary="Listar templates",
    description="Lista todos los templates configurados.",
)
async def list_templates(repo=Depends(get_template_repository)):
    templates = repo.get_all()
    return [
        {
            "id": t.id,
            "name": t.name,
            "file_path": t.file_path,
            "created_at": t.created_at.isoformat() if t.created_at else None,
        }
        for t in templates
    ]
