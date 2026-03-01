# API routes mínimas
import json
import logging
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import Response

from infrastructure.controllers.hello.hello_get_controller import HelloGetController
from infrastructure.controllers.health.health_controller import HealthController
from infrastructure.controllers.template.label_preview.preview_label_controller import PreviewLabelController
from infrastructure.controllers.printer.get_status.get_status_controller import GetStatusController
from infrastructure.controllers.printer.get_one_status_by_name.get_one_status_by_name_controller import GetOneStatusByNameController
from infrastructure.controllers.printer.discover.discover_printer_controller import DiscoverPrinterController
from infrastructure.controllers.template.remito_preview.preview_remito_controller import PreviewRemitoController
from infrastructure.controllers.print_jobs.create.create_print_job_controller import CreatePrintJobController
from infrastructure.controllers.channels.create.create_channel_controller import CreateChannelController
from infrastructure.controllers.printer.test.test_printer_controller import TestPrinterController
from infrastructure.api.container import container
from domain.repositories.printer_repository import PrinterRepository
from domain.repositories.channel_repository import ChannelRepository
from domain.repositories.template_repository import TemplateRepository

# DTOs
from infrastructure.dtos.channels.create.request import CreateChannelRequestDTO
from infrastructure.dtos.channels.create.response import CreateChannelResponseDTO
from infrastructure.dtos.channels.update.request import UpdateChannelRequestDTO
from infrastructure.dtos.printers.create.request import CreatePrinterRequestDTO
from infrastructure.dtos.printers.update.request import UpdatePrinterRequestDTO
from infrastructure.dtos.print_jobs.create.request import CreatePrintJobRequestDTO
from infrastructure.dtos.print_jobs.create.response import CreatePrintJobResponseDTO
from infrastructure.dtos.printer.discover.response import DiscoverPrinterResponseDTO
from infrastructure.dtos.printer.get_one_status_by_name.response import GetOneStatusByNameResponseDTO
from infrastructure.dtos.printer.get_status.response import GetStatusResponseDTO
from infrastructure.dtos.template.label_preview.request import LabelPreviewRequestDTO
from infrastructure.dtos.template.remito_preview.request import RemitoPreviewRequestDTO
from infrastructure.dtos.printer.test.response import TestPrinterResponseDTO

from pydantic import BaseModel
from datetime import datetime
from typing import Any, Dict, Optional
from sqlmodel import select, and_, desc

logger = logging.getLogger(__name__)
router = APIRouter()


def get_printer_repository() -> PrinterRepository:
    from infrastructure.db.database import engine
    return PrinterRepository(engine)


def get_channel_repository() -> ChannelRepository:
    from infrastructure.db.database import engine
    return ChannelRepository(engine)


def get_template_repository():
    from infrastructure.db.database import engine
    return TemplateRepository(engine)


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
    "/templates/remito/preview",
    tags=["Templates"],
    summary="Preview template remito (PDF)",
    description="Genera un PDF de remito para preview.",
    response_class=Response,
)
async def remito_preview(
    body: RemitoPreviewRequestDTO,
    format: str = Query("binary", description="binary (PDF) o json (base64)"),
    controller: PreviewRemitoController = Depends(container.remito_preview_controller),
):
    return controller(body, format=format)


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
    controller: PreviewLabelController = Depends(container.preview_label_controller),
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
    response_model=TestPrinterResponseDTO,
)
async def test_printer(
    printer_id: int,
    controller: TestPrinterController = Depends(container.test_printer_controller),
):
    return controller(printer_id)


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
