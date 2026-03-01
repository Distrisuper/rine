from typing import Optional, List
from application.use_cases.printer.update.update_printer_use_case_interface import UpdatePrinterUseCaseInterface

class UpdatePrinterController:
    def __init__(self, use_case: UpdatePrinterUseCaseInterface):
        self._use_case = use_case

    def __call__(self, printer_id: int, name: str = '', is_active: Optional[bool] = None, channel_ids: Optional[List[int]] = None) -> Optional[dict]:
        return self._use_case(printer_id, name, is_active, channel_ids)
