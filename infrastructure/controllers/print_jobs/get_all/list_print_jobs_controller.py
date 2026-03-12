from datetime import datetime
from typing import Optional, Dict
from application.use_cases.print_jobs.get_all.list_print_jobs_use_case_interface import ListPrintJobsUseCaseInterface

class ListPrintJobsController:
    def __init__(self, use_case: ListPrintJobsUseCaseInterface):
        self._use_case = use_case

    def __call__(
        self,
        printer_name: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 100
    ) -> Dict:
        data, total = self._use_case(
            printer_name=printer_name,
            date_from=date_from,
            date_to=date_to,
            status=status,
            page=page,
            limit=limit
        )
        
        return {
            "data": data,
            "page": page,
            "limit": limit,
            "total": total
        }
