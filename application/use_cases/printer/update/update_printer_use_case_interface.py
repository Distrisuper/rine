from abc import ABC, abstractmethod
from typing import List, Optional

class UpdatePrinterUseCaseInterface(ABC):
    @abstractmethod
    def __call__(self, printer_id: int, name: str = '', is_active: Optional[bool] = None, channel_ids: Optional[List[int]] = None) -> Optional[dict]:
        pass
