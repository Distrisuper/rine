# API routes mínimas
from fastapi import APIRouter, Depends, HTTPException
from app.controllers.hello_controller import HelloController
from app.controllers.print_controller import PrintController
from app.controllers.printer_controller import PrinterController
from app.models import PrintRequest, PrintResponse
from app.services.print_service import PrintService
from app.adapters.sqlite_repository import SqliteRepository
from app.adapters.cups_printer_discovery import CupsPrinterDiscovery
from app.interfaces.print_job_repository import PrintJobRepository
from app.interfaces.printer_discovery import PrinterDiscovery
from app.config import get_settings
from app.config import Settings

router = APIRouter()


def get_printer_discovery() -> PrinterDiscovery:
    """Dependencia: implementación por defecto (CUPS o mock)."""
    return CupsPrinterDiscovery()


def get_sqlite_repository(settings: Settings = Depends(get_settings)) -> SqliteRepository:
    """Dependencia: repositorio SQLite."""
    return SqliteRepository(settings.sqlite_db_path)


def get_print_job_repository(
    repository: SqliteRepository = Depends(get_sqlite_repository),
) -> PrintJobRepository:
    """Dependencia: repositorio de trabajos de impresion."""
    return repository


def get_print_service(repository: PrintJobRepository = Depends(get_print_job_repository)) -> PrintService:
    """Dependencia: servicio de impresion con SQLite."""
    return PrintService(repository)

@router.get("/")
async def root():
    return HelloController.root()

@router.get("/health")
async def health():
    return HelloController.health()

@router.post(
    "/print",
    response_model=PrintResponse,
    summary="Encola comprobante",
    description="""
Endpoint unificado para imprimir diferentes tipos de comprobantes.

## Tipos disponibles:

### 🏷️ ETIQ (Etiqueta de envío)
Campos requeridos adicionales:
- `client_address`
- `client_city` 
- `package_quantity`
- `label_packages`

### 📄 REMI (Remito de entrega)
Campos requeridos adicionales:
- `client_address`
- `client_city`
- `remitos_quantity`
- `label_packages`

### 📋 GM (Pedido de impresión)
Campos requeridos adicionales:
- `invoices_quantity`

### ⏳ PEND (Redi pendiente)
Campos requeridos adicionales:
- `package_quantity`
- `pending`

---

**Campos base siempre requeridos:** `type`, `client_code`, `client_name`, `redi_code`, `id_remito`
""",
    responses={
        200: {
            "description": "Solicitud encolada exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "ok": 1,
                        "message": "Solicitud encolada para cliente CL001 (Distribuidora ABC)...",
                        "doc_type": "etiqueta"
                    }
                }
            }
        },
        400: {
            "description": "Error de validación: tipo inválido o campos requeridos faltantes",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_type": {
                            "summary": "Tipo inválido",
                            "value": {"detail": "Tipo de impresión inválido: INVALID"}
                        },
                        "missing_fields": {
                            "summary": "Campos faltantes",
                            "value": {"detail": "ETIQ requiere: client_address, client_city, package_quantity, label_packages"}
                        }
                    }
                }
            }
        }
    }
)
async def print_document(
    request: PrintRequest,
    service: PrintService = Depends(get_print_service),
) -> PrintResponse:
    """Encola impresión según tipo de comprobante."""
    try:
        return await PrintController.process_print(service, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
# --- Monitoreo de impresoras (CUPS) - testing por interfaz ---
@router.get(
    "/printers/status",
    summary="Estado de la flota de impresoras",
    description="Lista todas las impresoras detectadas por CUPS con ready/not_ready y detalles. En Windows devuelve _cups_unavailable.",
)
async def printers_status(discovery: PrinterDiscovery = Depends(get_printer_discovery)):
    return PrinterController.get_status(discovery)


@router.get(
    "/printers/status/{name}",
    summary="Estado de una impresora",
    description="Estado de la impresora por nombre. 404 si no existe o CUPS no disponible.",
)
async def printer_status(name: str, discovery: PrinterDiscovery = Depends(get_printer_discovery)):
    data = PrinterController.get_printer_status(discovery, name)
    if data is None:
        raise HTTPException(status_code=404, detail="Impresora no encontrada o CUPS no disponible")
    return data
