from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Tuple
from domain.entities.print_job import PrintJob

class PrintJobRepositoryInterface(ABC):
    @abstractmethod
    def create(self, job: PrintJob) -> PrintJob:
        pass

    @abstractmethod
    def get_by_id(self, job_id: int) -> Optional[PrintJob]:
        pass

    @abstractmethod
    def update(self, job: PrintJob) -> PrintJob:
        pass

    @abstractmethod
    def get_all(
        self,
        printer_name: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 100
    ) -> Tuple[List[PrintJob], int]:
        pass
