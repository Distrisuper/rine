from application.use_cases.printer.delete.delete_printer_use_case_interface import DeletePrinterUseCaseInterface
from domain.repositories.printer_repository_interface import PrinterRepositoryInterface

class DeletePrinterUseCase(DeletePrinterUseCaseInterface):
    def __init__(self, repo: PrinterRepositoryInterface):
        self._repo = repo

    def __call__(self, printer_id: int) -> bool:
        success = self._repo.delete_printer(printer_id)
        if not success:
            raise ValueError("Impresora no encontrada")
        return True
