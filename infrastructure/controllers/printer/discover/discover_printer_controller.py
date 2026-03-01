from application.use_cases.printer.discover.discover_printer_use_case_interface import (
    DiscoverPrinterUseCaseInterface,
)


class DiscoverPrinterController:
    def __init__(self, use_case: DiscoverPrinterUseCaseInterface):
        self._use_case = use_case

    def __call__(self) -> list[dict]:
        return self._use_case()
