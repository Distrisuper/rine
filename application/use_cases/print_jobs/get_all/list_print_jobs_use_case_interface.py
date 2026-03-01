from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Tuple, List

class ListPrintJobsUseCaseInterface(ABC):
    @abstractmethod
    def __call__(
        self,
        printer_name: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 100
    ) -> Tuple[List[dict], int]:
        pass
