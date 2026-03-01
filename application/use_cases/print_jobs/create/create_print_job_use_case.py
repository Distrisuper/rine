import json
from datetime import datetime

from application.use_cases.print_jobs.create.create_print_job_use_case_interface import (
    CreatePrintJobUseCaseInterface,
)
from domain.entities.print_job import PrintJob
from sqlmodel import Session
from infrastructure.db.database import engine


class CreatePrintJobUseCase(CreatePrintJobUseCaseInterface):
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

        with Session(engine) as session:
            session.add(job)
            session.commit()
            session.refresh(job)

        return {
            "id": job.id,
            "client_code": job.client_code,
            "client_name": job.client_name,
            "channel": job.channel,
            "status": job.status,
            "print_count": job.print_count,
            "print_type": job.print_type,
            "date_created": job.date_created,
            "date_started": job.date_started,
            "date_processed": job.date_processed,
            "printer_name": job.printer_name,
            "error_message": job.error_message,
        }
