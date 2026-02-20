from app.models import PrintRequest, PrintResponse


class PrintService:
    """Servicio para gestionar impresiones."""

    def __init__(self) -> None:
        """Inicializa el servicio de impresión (punto de inyección de dependencias futuro)."""
        # Actualmente no hay dependencias externas. Este constructor existe
        # para mantener consistencia con otros servicios y facilitar
        # la futura inyección de dependencias (por ejemplo, clientes HTTP,
        # configuración, etc.).

    async def process_print(self, request: PrintRequest) -> PrintResponse:
        """Procesa solicitud de impresión según tipo."""
        print_type = request.type

        if print_type == "ETIQ":
            return await self._print_label(request)
        elif print_type == "REMI":
            return await self._print_remito(request)
        elif print_type == "GM":
            return await self._print_gm_request(request)
        elif print_type == "PEND":
            return await self._print_pending_redi(request)

    async def _print_label(self, request: PrintRequest) -> PrintResponse:
        """Procesa solicitud de impresión de etiqueta."""
        if not all([
            request.client_address is not None,
            request.client_city is not None,
            request.package_quantity is not None,
            request.label_packages is not None
        ]):
            raise ValueError("ETIQ requiere: client_address, client_city, package_quantity, label_packages")

        message = (
            f"Imprimiendo etiqueta para cliente {request.client_code} ({request.client_name}). "
            f"Dirección: {request.client_address}, {request.client_city}. "
            f"Cantidad de paquetes: {request.package_quantity}. "
            f"Código REDI: {request.redi_code}. Host: {request.set_host}."
        )
        return PrintResponse(ok=1, message=message, doc_type="etiqueta")

    async def _print_remito(self, request: PrintRequest) -> PrintResponse:
        """Procesa solicitud de impresión de remito."""
        if not all([
            request.client_address is not None,
            request.client_city is not None,
            request.location is not None,
            request.remitos_quantity is not None,
            request.label_packages is not None
        ]):
            raise ValueError("REMI requiere: client_address, client_city, location, remitos_quantity, label_packages")

        message = (
            f"Imprimiendo remito para cliente {request.client_code} ({request.client_name}). "
            f"Cantidad de remitos: {request.remitos_quantity}. "
            f"ID Remito: {request.id_remito}. "
            f"Ubicación: {request.location}. Host: {request.set_host}."
        )
        return PrintResponse(ok=1, message=message, doc_type="remito")

    async def _print_gm_request(self, request: PrintRequest) -> PrintResponse:
        """Procesa solicitud de impresión de pedido GM."""
        if not all([
            request.location is not None,
            request.invoices_quantity is not None
        ]):
            raise ValueError("GM requiere: location, invoices_quantity")

        message = (
            f"Imprimiendo pedido GM para cliente {request.client_code} ({request.client_name}). "
            f"Cantidad de comprobantes: {request.invoices_quantity}. "
            f"ID Remito: {request.id_remito}. Ubicación: {request.location}. Host: {request.set_host}."
        )
        return PrintResponse(ok=1, message=message, doc_type="pedido de impresión")

    async def _print_pending_redi(self, request: PrintRequest) -> PrintResponse:
        """Procesa solicitud de impresión de redi pendiente."""
        if not all([
            request.location is not None,
            request.package_quantity is not None,
            request.pending is not None
        ]):
            raise ValueError("PEND requiere: location, package_quantity, pending")

        pending_label = "pendiente" if request.pending else "no pendiente"
        message = (
            f"Imprimiendo redi pendiente para cliente {request.client_code} ({request.client_name}). "
            f"Estado: {pending_label}. Cantidad de paquetes: {request.package_quantity}. "
            f"ID Remito: {request.id_remito}. Código REDI: {request.redi_code}."
        )
        return PrintResponse(ok=1, message=message, doc_type="redi pendiente")
