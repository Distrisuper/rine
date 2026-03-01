from datetime import datetime
from typing import Optional, Tuple, List
from application.use_cases.print_jobs.get_all.list_print_jobs_use_case_interface import ListPrintJobsUseCaseInterface
from domain.repositories.print_job_repository_interface import PrintJobRepositoryInterface

class ListPrintJobsUseCase(ListPrintJobsUseCaseInterface):
    def __init__(self, repo: PrintJobRepositoryInterface):
        self._repo = repo

    def __call__(
        self,
        printer_name: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 100
    ) -> Tuple[List[dict], int]:
        jobs, total = self._repo.get_all(
            printer_name=printer_name,
            date_from=date_from,
            date_to=date_to,
            status=status,
            page=page,
            limit=limit
        )
        
        data = [
            {
                "id": j.id,
                "client_code": j.client_code,
                "client_name": j.client_name,
                "channel": j.channel,
                "status": j.status,
                "print_count": j.print_count,
                "print_type": j.print_type,
                "date_created": j.date_created,
                "date_started": j.date_started,
                "date_processed": j.date_processed,
                "printer_name": j.printer_name,
                "error_message": j.error_message,
            }
            for j in jobs
        ]
        
        return data, total
