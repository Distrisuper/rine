from datetime import datetime, timezone
import json

from app.interfaces.print_job_repository import PrintJobRepository
from app.models import PrintJobStatus, PrintRequest, PrintResponse


class PrintService:
    """Servicio para gestionar impresiones."""

    def __init__(self, repository: PrintJobRepository):
        self._repository = repository

    async def process_print(self, request: PrintRequest) -> PrintResponse:
        """Encola solicitud de impresión según tipo."""
        self._validate_request(request)
        created_at = self._utc_now_iso()
        print_count = self._resolve_print_count(request)
        payload = json.dumps(request.model_dump(), ensure_ascii=True)
        await self._repository.enqueue_job(
            request=request,
            status=PrintJobStatus.PENDIENTE,
            created_at=created_at,
            print_count=print_count,
            payload=payload,
        )
        return self._queued_response(request)

    def _validate_request(self, request: PrintRequest) -> None:
        print_type = request.type.upper()

        if print_type == "ETIQ":
            self._validate_label(request)
            return
        if print_type == "REMI":
            self._validate_remito(request)
            return
        if print_type == "GM":
            self._validate_gm_request(request)
            return
        if print_type == "PEND":
            self._validate_pending_redi(request)
            return

        raise ValueError(f"Tipo de impresión inválido: {request.type}")

    @staticmethod
    def _validate_label(request: PrintRequest) -> None:
        if not all([
            request.client_address is not None,
            request.client_city is not None,
            request.package_quantity is not None,
            request.label_packages is not None
        ]):
            raise ValueError("ETIQ requiere: client_address, client_city, package_quantity, label_packages")

    @staticmethod
    def _validate_remito(request: PrintRequest) -> None:
        if not all([
            request.client_address is not None,
            request.client_city is not None,
            request.remitos_quantity is not None,
            request.label_packages is not None
        ]):
            raise ValueError("REMI requiere: client_address, client_city, remitos_quantity, label_packages")

    @staticmethod
    def _validate_gm_request(request: PrintRequest) -> None:
        if not all([
            request.invoices_quantity is not None
        ]):
            raise ValueError("GM requiere: invoices_quantity")

    @staticmethod
    def _validate_pending_redi(request: PrintRequest) -> None:
        if not all([
            request.package_quantity is not None,
            request.pending is not None
        ]):
            raise ValueError("PEND requiere: package_quantity, pending")

    @staticmethod
    def _queued_response(request: PrintRequest) -> PrintResponse:
        doc_type = PrintService._doc_type_for(request.type)
        message = (
            f"Solicitud encolada para cliente {request.client_code} ({request.client_name}). "
            f"Tipo: {doc_type}."
        )
        return PrintResponse(ok=1, message=message, doc_type=doc_type)

    @staticmethod
    def _resolve_print_count(request: PrintRequest) -> int:
        print_type = request.type.upper()

        if print_type == "ETIQ":
            return int(request.label_packages or 0)
        if print_type == "REMI":
            return int(request.remitos_quantity or 0)
        if print_type == "GM":
            return int(request.invoices_quantity or 0)
        if print_type == "PEND":
            return int(request.package_quantity or 0)

        return 0

    @staticmethod
    def _doc_type_for(print_type: str) -> str:
        mapping = {
            "ETIQ": "etiqueta",
            "REMI": "remito",
            "GM": "pedido de impresión",
            "PEND": "redi pendiente",
        }
        return mapping.get(print_type.upper(), "desconocido")

    @staticmethod
    def _utc_now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()
