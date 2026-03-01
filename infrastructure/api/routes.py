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
from infrastructure.controllers.printer.get_all.list_printers_controller import ListPrintersController
from infrastructure.controllers.printer.create.create_printer_controller import CreatePrinterController
from infrastructure.controllers.printer.update.update_printer_controller import UpdatePrinterController
from infrastructure.controllers.printer.delete.delete_printer_controller import DeletePrinterController
from infrastructure.controllers.template.remito_preview.preview_remito_controller import PreviewRemitoController
from infrastructure.controllers.template.get_all.list_templates_controller import ListTemplatesController
from infrastructure.controllers.print_jobs.create.create_print_job_controller import CreatePrintJobController
from infrastructure.controllers.print_jobs.get_all.list_print_jobs_controller import ListPrintJobsController
from infrastructure.controllers.channels.create.create_channel_controller import CreateChannelController
from infrastructure.controllers.channels.get_all.list_channels_controller import ListChannelsController
from infrastructure.controllers.channels.update.update_channel_controller import UpdateChannelController
from infrastructure.controllers.channels.delete.delete_channel_controller import DeleteChannelController
from infrastructure.controllers.printer.test.test_printer_controller import TestPrinterController
from infrastructure.api.container import container

# DTOs
from infrastructure.dtos.channels.create.request import CreateChannelRequestDTO
from infrastructure.dtos.channels.create.response import CreateChannelResponseDTO
from infrastructure.dtos.channels.update.request import UpdateChannelRequestDTO
from infrastructure.dtos.channels.update.response import UpdateChannelResponseDTO
from infrastructure.dtos.channels.get_all.response import ListChannelResponseDTO
from infrastructure.dtos.channels.delete.response import DeleteChannelResponseDTO
from infrastructure.dtos.printers.create.request import CreatePrinterRequestDTO
from infrastructure.dtos.printers.update.request import UpdatePrinterRequestDTO
from infrastructure.dtos.printers.response import PrinterResponseDTO
from infrastructure.dtos.print_jobs.create.request import CreatePrintJobRequestDTO
from infrastructure.dtos.print_jobs.create.response import CreatePrintJobResponseDTO
from infrastructure.dtos.print_jobs.list.response import PaginatedPrintJobsResponseDTO
from infrastructure.dtos.printer.discover.response import DiscoverPrinterResponseDTO
from infrastructure.dtos.printer.get_one_status_by_name.response import GetOneStatusByNameResponseDTO
from infrastructure.dtos.printer.get_status.response import GetStatusResponseDTO
from infrastructure.dtos.template.label_preview.request import LabelPreviewRequestDTO
from infrastructure.dtos.template.remito_preview.request import RemitoPreviewRequestDTO
from infrastructure.dtos.template.list.response import TemplateResponseDTO
from infrastructure.dtos.printer.test.response import TestPrinterResponseDTO
from infrastructure.dtos.health.response import HealthResponseDTO
from infrastructure.dtos.hello.get.response import HelloGetResponseDTO

from datetime import datetime
from typing import List, Optional

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", tags=["Health"], response_model=HelloGetResponseDTO)
async def root(controller: HelloGetController = Depends(container.hello_controller)):
    return controller()


@router.get("/health", tags=["Health"], response_model=HealthResponseDTO)
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
    response_model=PaginatedPrintJobsResponseDTO,
)
async def list_print_jobs(
    printer_name: Optional[str] = Query(None, description="Filtrar por nombre de impresora"),
    date_from: Optional[datetime] = Query(None, description="Fecha inicio (ISO)"),
    date_to: Optional[datetime] = Query(None, description="Fecha fin (ISO)"),
    status: Optional[str] = Query(None, description="Filtrar por status: pending, printed, failed"),
    page: int = Query(1, ge=1, description="Página"),
    limit: int = Query(100, ge=1, le=500, description="Registros por página"),
    controller: ListPrintJobsController = Depends(container.list_print_jobs_controller),
):
    return controller(
        printer_name=printer_name,
        date_from=date_from,
        date_to=date_to,
        status=status,
        page=page,
        limit=limit
    )


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
    response_model=List[PrinterResponseDTO],
)
async def list_printers(
    controller: ListPrintersController = Depends(container.list_printers_controller),
):
    return controller()


@router.post(
    "/printers",
    tags=["Printers"],
    summary="Crear impresora",
    description="Crea una nueva impresora con channels asociados.",
    response_model=PrinterResponseDTO,
)
async def create_printer(
    body: CreatePrinterRequestDTO,
    controller: CreatePrinterController = Depends(container.create_printer_controller),
):
    return controller(body.name, body.channel_ids or [])


@router.put(
    "/printers/{printer_id}",
    tags=["Printers"],
    summary="Editar impresora",
    description="Edita una impresora y sus channels.",
    response_model=PrinterResponseDTO,
)
async def update_printer(
    printer_id: int,
    body: UpdatePrinterRequestDTO,
    controller: UpdatePrinterController = Depends(container.update_printer_controller),
):
    return controller(
        printer_id=printer_id,
        name=body.name,
        is_active=body.is_active,
        channel_ids=body.channel_ids,
    )


@router.delete(
    "/printers/{printer_id}",
    tags=["Printers"],
    summary="Eliminar impresora",
    description="Elimina una impresora y sus channels asociados.",
)
async def delete_printer(
    printer_id: int,
    controller: DeletePrinterController = Depends(container.delete_printer_controller),
):
    return controller(printer_id)


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
    response_model=List[ListChannelResponseDTO],
)
async def list_channels(
    controller: ListChannelsController = Depends(container.list_channels_controller),
):
    return controller()


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
    response_model=UpdateChannelResponseDTO,
)
async def update_channel(
    channel_id: int,
    body: UpdateChannelRequestDTO,
    controller: UpdateChannelController = Depends(container.update_channel_controller),
):
    return controller(
        channel_id=channel_id,
        description=body.description,
        is_active=body.is_active,
        template_id=body.template_id,
    )


@router.delete(
    "/channels/{channel_id}",
    tags=["Channels"],
    summary="Eliminar channel",
    description="Elimina un channel.",
    response_model=DeleteChannelResponseDTO,
)
async def delete_channel(
    channel_id: int,
    controller: DeleteChannelController = Depends(container.delete_channel_controller),
):
    return controller(channel_id)


# Templates endpoints
@router.get(
    "/templates",
    tags=["Templates"],
    summary="Listar templates",
    description="Lista todos los templates configurados.",
    response_model=List[TemplateResponseDTO],
)
async def list_templates(
    controller: ListTemplatesController = Depends(container.list_templates_controller),
):
    return controller()
