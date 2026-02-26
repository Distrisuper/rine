from typing import Any

from domain.services.printer_discovery import PrinterDiscovery
from application.use_cases.printer.discover.discover_printer_use_case_interface import (
    DiscoverPrinterUseCaseInterface,
)


class DiscoverPrinterUseCase(DiscoverPrinterUseCaseInterface):
    def __init__(self, printer_discovery: PrinterDiscovery):
        self._printer_discovery = printer_discovery

    def __call__(self) -> list[dict[str, Any]]:
        return self._printer_discovery.discover_printers()
