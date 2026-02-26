import json
from datetime import datetime

from application.use_cases.print_jobs.create.create_print_job_use_case_interface import (
    CreatePrintJobUseCaseInterface,
)
from domain.entities.print_job import PrintJob
from domain.entities.document_type import get_document_type
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
        doc_type = get_document_type(channel)

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
            "status": job.status,
            "date_created": job.date_created.isoformat(),
            "document_type": f"channel_{channel}",
        }
