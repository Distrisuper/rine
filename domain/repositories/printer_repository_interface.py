from abc import ABC, abstractmethod
from typing import Optional, List
from domain.entities.printer import Printer
from domain.value_objects import PrinterConfig

class PrinterRepositoryInterface(ABC):
    @abstractmethod
    def get_printer_for_channel(self, channel: int) -> Optional[PrinterConfig]:
        pass

    @abstractmethod
    def get_all_printers(self) -> List[Printer]:
        pass

    @abstractmethod
    def get_printer_by_id(self, printer_id: int) -> Optional[Printer]:
        pass

    @abstractmethod
    def create_printer(self, name: str, channel_ids: Optional[List[int]] = None) -> dict:
        pass

    @abstractmethod
    def update_printer(self, printer_id: int, name: str = '', is_active: Optional[bool] = None) -> Optional[dict]:
        pass

    @abstractmethod
    def set_printer_channels(self, printer_id: int, channel_ids: List[int]) -> bool:
        pass

    @abstractmethod
    def get_printer_channels(self, printer_id: int) -> List[dict]:
        pass

    @abstractmethod
    def get_all_printers_with_channels(self) -> List[dict]:
        pass

    @abstractmethod
    def get_all_channels_with_printers(self) -> List[dict]:
        pass

    @abstractmethod
    def delete_printer(self, printer_id: int) -> bool:
        pass
