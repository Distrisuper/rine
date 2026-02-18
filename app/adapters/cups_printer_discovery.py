"""Adaptador que implementa PrinterDiscovery usando el servicio CUPS (o mock en Windows)."""
from typing import Any

from app.interfaces.printer_discovery import PrinterDiscovery
from app.services import printer_discovery_service


class CupsPrinterDiscovery(PrinterDiscovery):
    """Implementación vía CUPS; en Windows sin pycups usa mock si RINE_MOCK_PRINTERS=1."""

    def get_flota_status(self) -> dict[str, Any]:
        return printer_discovery_service.monitorear_flota()

    def get_printer_status(self, name: str) -> dict[str, Any] | None:
        return printer_discovery_service.estado_impresora(name)
