from typing import List, Optional
from application.use_cases.printer.update.update_printer_use_case_interface import UpdatePrinterUseCaseInterface
from domain.repositories.printer_repository import PrinterRepository

class UpdatePrinterUseCase(UpdatePrinterUseCaseInterface):
    def __init__(self, repo: PrinterRepository):
        self._repo = repo

    def __call__(self, printer_id: int, name: str = '', is_active: Optional[bool] = None, channel_ids: Optional[List[int]] = None) -> Optional[dict]:
        printer = self._repo.update_printer(
            printer_id,
            name=name,
            is_active=is_active,
        )
        
        if not printer:
            return None
        
        if channel_ids is not None:
            self._repo.set_printer_channels(printer_id, channel_ids)
            # Refrescar los canales en la respuesta
            printer["channels"] = self._repo.get_printer_channels(printer_id)
        
        return printer
