from application.use_cases.printer.delete.delete_printer_use_case_interface import DeletePrinterUseCaseInterface
from domain.repositories.printer_repository import PrinterRepository

class DeletePrinterUseCase(DeletePrinterUseCaseInterface):
    def __init__(self, repo: PrinterRepository):
        self._repo = repo

    def __call__(self, printer_id: int) -> bool:
        return self._repo.delete_printer(printer_id)
