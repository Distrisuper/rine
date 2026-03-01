from typing import List
from application.use_cases.printer.create.create_printer_use_case_interface import CreatePrinterUseCaseInterface

class CreatePrinterController:
    def __init__(self, use_case: CreatePrinterUseCaseInterface):
        self._use_case = use_case

    def __call__(self, name: str, channel_ids: List[int]) -> dict:
        return self._use_case(name, channel_ids)
