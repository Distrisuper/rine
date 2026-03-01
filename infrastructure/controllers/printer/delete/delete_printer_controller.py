from application.use_cases.printer.delete.delete_printer_use_case_interface import DeletePrinterUseCaseInterface

class DeletePrinterController:
    def __init__(self, use_case: DeletePrinterUseCaseInterface):
        self._use_case = use_case

    def __call__(self, printer_id: int) -> bool:
        return self._use_case(printer_id)
