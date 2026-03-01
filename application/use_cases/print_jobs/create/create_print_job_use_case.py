import json
from datetime import datetime
from application.use_cases.print_jobs.create.create_print_job_use_case_interface import (
    CreatePrintJobUseCaseInterface,
)
from domain.entities.print_job import PrintJob
from domain.repositories.print_job_repository import PrintJobRepository

class CreatePrintJobUseCase(CreatePrintJobUseCaseInterface):
    def __init__(self, repo: PrintJobRepository):
        self._repo = repo

    def __call__(
        self,
        channel: int,
        client_code: str,
        client_name: str,
        payload: dict,
    ) -> dict:
        job = PrintJob(
            client_code=client_code,
            client_name=client_name,
            channel=channel,
            payload=json.dumps(payload),
            status="pending",
            print_count=0,
            date_created=datetime.utcnow(),
        )

        saved_job = self._repo.create(job)

        return {
            "id": saved_job.id,
            "client_code": saved_job.client_code,
            "client_name": saved_job.client_name,
            "channel": saved_job.channel,
            "status": saved_job.status,
            "print_count": saved_job.print_count,
            "print_type": saved_job.print_type,
            "date_created": saved_job.date_created,
            "date_started": saved_job.date_started,
            "date_processed": saved_job.date_processed,
            "printer_name": saved_job.printer_name,
            "error_message": saved_job.error_message,
        }
