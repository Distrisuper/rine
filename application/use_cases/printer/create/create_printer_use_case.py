from typing import List
from application.use_cases.printer.create.create_printer_use_case_interface import CreatePrinterUseCaseInterface
from domain.repositories.printer_repository import PrinterRepository

class CreatePrinterUseCase(CreatePrinterUseCaseInterface):
    def __init__(self, repo: PrinterRepository):
        self._repo = repo

    def __call__(self, name: str, channel_ids: List[int]) -> dict:
        return self._repo.create_printer(name, channel_ids)
