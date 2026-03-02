from application.use_cases.printer.print_test_page.print_test_page_use_case_interface import PrintTestPageUseCaseInterface

class PrintTestPageController:
    def __init__(self, use_case: PrintTestPageUseCaseInterface):
        self._use_case = use_case

    def __call__(self, printer_id: int) -> dict:
        return self._use_case(printer_id)
