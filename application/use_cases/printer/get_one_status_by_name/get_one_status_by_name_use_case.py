from domain.services.printer_discovery_interface import PrinterDiscovery
from application.use_cases.printer.get_one_status_by_name.get_one_status_by_name_use_case_interface import GetOneStatusByNameUseCaseInterface


class GetOneStatusByNameUseCase(GetOneStatusByNameUseCaseInterface):
    def __init__(self, discovery: PrinterDiscovery):
        self._discovery = discovery

    def __call__(self, name: str) -> dict:
        data = self._discovery.get_printer_status(name)
        if data is None:
            raise ValueError("Impresora no encontrada o CUPS no disponible")
        return data
