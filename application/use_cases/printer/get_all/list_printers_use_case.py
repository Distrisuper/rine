from typing import List
from application.use_cases.printer.get_all.list_printers_use_case_interface import ListPrintersUseCaseInterface
from domain.repositories.printer_repository import PrinterRepository

class ListPrintersUseCase(ListPrintersUseCaseInterface):
    def __init__(self, repo: PrinterRepository):
        self._repo = repo

    def __call__(self) -> List[dict]:
        return self._repo.get_all_printers_with_channels()
