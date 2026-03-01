from application.use_cases.printer.test.test_printer_use_case_interface import TestPrinterUseCaseInterface

class TestPrinterController:
    def __init__(self, use_case: TestPrinterUseCaseInterface):
        self._use_case = use_case

    def __call__(self, printer_id: int) -> dict:
        return self._use_case(printer_id)
