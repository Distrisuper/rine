import json
from fastapi import APIRouter, Depends, status, Query, HTTPException
from typing import List, Optional
from datetime import datetime

from infrastructure.api.container import container

# Controllers
from infrastructure.controllers.printer.create.create_printer_controller import CreatePrinterController
from infrastructure.controllers.printer.get_all.list_printers_controller import ListPrintersController
from infrastructure.controllers.printer.get_status.get_status_controller import GetStatusController
from infrastructure.controllers.printer.update.update_printer_controller import UpdatePrinterController
from infrastructure.controllers.printer.get_one_status_by_name.get_one_status_by_name_controller import GetOneStatusByNameController
from infrastructure.controllers.printer.delete.delete_printer_controller import DeletePrinterController
from infrastructure.controllers.printer.discover.discover_printer_controller import DiscoverPrinterController
from infrastructure.controllers.printer.print_test_page.print_test_page_controller import PrintTestPageController

from infrastructure.controllers.channels.get_all.list_channels_controller import ListChannelsController
from infrastructure.controllers.channels.create.create_channel_controller import CreateChannelController
from infrastructure.controllers.channels.update.update_channel_controller import UpdateChannelController
from infrastructure.controllers.channels.delete.delete_channel_controller import DeleteChannelController

from infrastructure.controllers.template.get_all.list_templates_controller import ListTemplatesController
from infrastructure.controllers.template.label_preview.preview_label_controller import PreviewLabelController
from infrastructure.controllers.template.remito_preview.preview_remito_controller import PreviewRemitoController

from infrastructure.controllers.print_jobs.get_all.list_print_jobs_controller import ListPrintJobsController
from infrastructure.controllers.print_jobs.create.create_print_job_controller import CreatePrintJobController
from infrastructure.controllers.print_jobs.print.print_job_controller import PrintJobController

from infrastructure.controllers.health.health_controller import HealthController
from infrastructure.controllers.example.example_get_controller import ExampleGetController

# DTOs - Printers
from infrastructure.dtos.printers.create.request import CreatePrinterRequestDTO as CreatePrinterRequest
from infrastructure.dtos.printers.response import PrinterResponseDTO as PrinterResponse
from infrastructure.dtos.printers.update.request import UpdatePrinterRequestDTO as UpdatePrinterRequest
from infrastructure.dtos.printer.get_one_status_by_name.response import GetOneStatusByNameResponseDTO

# DTOs - Channels
from infrastructure.dtos.channels.create.request import CreateChannelRequestDTO as CreateChannelRequest
from infrastructure.dtos.channels.create.response import CreateChannelResponseDTO as CreateChannelResponse
from infrastructure.dtos.channels.get_all.response import ListChannelResponseDTO as ListChannelResponse
from infrastructure.dtos.channels.update.request import UpdateChannelRequestDTO as UpdateChannelRequest
from infrastructure.dtos.channels.update.response import UpdateChannelResponseDTO as UpdateChannelResponse

# DTOs - Print Jobs
from infrastructure.dtos.print_jobs.create.request import CreatePrintJobRequestDTO
from infrastructure.dtos.print_jobs.create.response import CreatePrintJobResponseDTO
from infrastructure.dtos.print_jobs.list.response import PaginatedPrintJobsResponseDTO
from infrastructure.dtos.print_jobs.print.request import PrintJobRequestDTO

# DTOs - Templates
from infrastructure.dtos.template.list.response import TemplateResponseDTO as TemplateResponse
from infrastructure.dtos.template.label_preview.request import LabelPreviewRequestDTO
from infrastructure.dtos.template.label_preview.response import LabelPreviewResponseDTO as LabelPreviewResponse
from infrastructure.dtos.template.remito_preview.request import RemitoPreviewRequestDTO
from infrastructure.dtos.template.remito_preview.response import RemitoPreviewResponseDTO as RemitoPreviewResponse

# DTOs - Health
from infrastructure.dtos.health.response import HealthResponseDTO

router = APIRouter()

# --- Health ---
@router.get("/health", tags=["Health"], response_model=HealthResponseDTO)
async def health(controller: HealthController = Depends(container.health_controller)):
    return controller()

# --- Example ---
@router.get("/example", tags=["Example"])
def example_flow(
    controller: ExampleGetController = Depends(container.example_controller)
):
    return controller()

# --- Printers ---
@router.get(
    "/printers",
    tags=["Printers"],
    summary="Listar impresoras",
    description="Obtiene todas las impresoras configuradas.",
    response_model=List[PrinterResponse]
)
def get_all_printers(
    controller: ListPrintersController = Depends(container.get_all_printers_controller)
):
    return controller()

@router.post(
    "/printers",
    tags=["Printers"],
    summary="Crear impresora",
    description="Crea una nueva impresora y la vincula con canales.",
    response_model=PrinterResponse
)
def create_printer(
    request: CreatePrinterRequest,
    controller: CreatePrinterController = Depends(container.create_printer_controller)
):
    return controller(request.name, request.channel_ids)

@router.put(
    "/printers/{printer_id}",
    tags=["Printers"],
    summary="Actualizar impresora",
    description="Actualiza nombre, estado y canales de una impresora.",
    response_model=PrinterResponse
)
def update_printer(
    printer_id: int,
    request: UpdatePrinterRequest,
    controller: UpdatePrinterController = Depends(container.update_printer_controller)
):
    return controller(printer_id, request.name, request.is_active, request.channel_ids)

@router.delete(
    "/printers/{printer_id}",
    tags=["Printers"],
    summary="Eliminar impresora",
    description="Elimina físicamente una impresora.",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_printer(
    printer_id: int,
    controller: DeletePrinterController = Depends(container.delete_printer_controller)
):
    controller(printer_id)
    return None

@router.get(
    "/printers/discover",
    tags=["Printers"],
    summary="Descubrir impresoras",
    description="Busca impresoras disponibles en el sistema (CUPS)."
)
def discover_printers(
    controller: DiscoverPrinterController = Depends(container.discover_printer_controller)
):
    return controller()

@router.get(
    "/printers/status",
    tags=["Printers"],
    summary="Estado de la flota",
    description="Estado actual de todas las impresoras en CUPS."
)
def get_printers_status(
    controller: GetStatusController = Depends(container.get_printer_status_controller)
):
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

# --- Channels ---
@router.get(
    "/channels",
    tags=["Channels"],
    summary="Listar canales",
    description="Obtiene todos los canales configurados.",
    response_model=List[ListChannelResponse]
)
def get_all_channels(
    controller: ListChannelsController = Depends(container.get_all_channels_controller)
):
    return controller()

@router.post(
    "/channels",
    tags=["Channels"],
    summary="Crear canal",
    description="Crea un nuevo canal vinculado a un template.",
    response_model=CreateChannelResponse
)
def create_channel(
    request: CreateChannelRequest,
    controller: CreateChannelController = Depends(container.create_channel_controller)
):
    return controller(request.channel_number, request.description, request.template_id)

@router.put(
    "/channels/{channel_id}",
    tags=["Channels"],
    summary="Actualizar canal",
    description="Actualiza descripción, estado y template de un canal.",
    response_model=UpdateChannelResponse
)
def update_channel(
    channel_id: int,
    request: UpdateChannelRequest,
    controller: UpdateChannelController = Depends(container.update_channel_controller)
):
    return controller(channel_id, request.description, request.is_active, request.template_id)

@router.delete(
    "/channels/{channel_id}",
    tags=["Channels"],
    summary="Eliminar canal",
    description="Elimina físicamente un canal.",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_channel(
    channel_id: int,
    controller: DeleteChannelController = Depends(container.delete_channel_controller)
):
    controller(channel_id)
    return None

# --- Templates ---
@router.get(
    "/templates",
    tags=["Templates"],
    summary="Listar templates",
    description="Obtiene todos los templates disponibles.",
    response_model=List[TemplateResponse]
)
def get_all_templates(
    controller: ListTemplatesController = Depends(container.get_all_templates_controller)
):
    return controller()

@router.get(
    "/templates/preview/label/{channel_number}",
    tags=["Templates"],
    summary="Preview de etiqueta (ZPL/PNG)"
)
def preview_label(
    channel_number: int,
    params: LabelPreviewRequestDTO = Depends(),
    controller: PreviewLabelController = Depends(container.label_preview_controller)
):
    params.channel = channel_number
    return controller(params)

@router.get(
    "/templates/preview/label/{channel_number}/json",
    tags=["Templates"],
    summary="Preview de etiqueta (JSON)",
    response_model=LabelPreviewResponse
)
def preview_label_json(
    channel_number: int,
    params: LabelPreviewRequestDTO = Depends(),
    controller: PreviewLabelController = Depends(container.label_preview_controller)
):
    params.channel = channel_number
    return controller(params, format="json")

@router.get(
    "/templates/preview/remito/{channel_number}",
    tags=["Templates"],
    summary="Preview de remito (PDF)"
)
def preview_remito(
    channel_number: int,
    params: RemitoPreviewRequestDTO = Depends(),
    controller: PreviewRemitoController = Depends(container.remito_preview_controller)
):
    params.channel = channel_number
    return controller(params)

@router.get(
    "/templates/preview/remito/{channel_number}/json",
    tags=["Templates"],
    summary="Preview de remito (JSON)",
    response_model=RemitoPreviewResponse
)
def preview_remito_json(
    channel_number: int,
    params: RemitoPreviewRequestDTO = Depends(),
    controller: PreviewRemitoController = Depends(container.remito_preview_controller)
):
    params.channel = channel_number
    return controller(params, format="json")

# --- Print Jobs ---
@router.get(
    "/print-jobs",
    tags=["PrintJobs"],
    summary="Listar trabajos",
    description="Lista trabajos con filtros y paginación.",
    response_model=PaginatedPrintJobsResponseDTO
)
def get_all_print_jobs(
    printer_name: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=500),
    controller: ListPrintJobsController = Depends(container.get_all_print_jobs_controller)
):
    return controller(printer_name, date_from, date_to, status, page, limit)

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

@router.post(
    "/print-jobs/print",
    tags=["PrintJobs"],
    summary="Impresión directa",
    description="Envía contenido base64 directamente a una impresora."
)
def print_raw(
    request: PrintJobRequestDTO,
    controller: PrintJobController = Depends(container.print_job_controller)
):
    return controller(
        printer_name=request.printer_name,
        content_base64=request.content_base64,
        content_type=request.content_type,
        job_title=request.job_title
    )

# --- Printer Test Page ---
@router.post(
    "/printers/{printer_id}/test",
    tags=["Printers"],
    summary="Impresión de prueba",
    description="Genera trabajos de prueba para todos los canales de la impresora."
)
def print_test_page(
    printer_id: int,
    controller: PrintTestPageController = Depends(container.print_test_page_controller)
):
    return controller(printer_id)
