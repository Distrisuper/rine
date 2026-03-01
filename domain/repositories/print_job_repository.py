from sqlmodel import Session, select
from typing import List, Optional
from domain.entities.print_job import PrintJob

class PrintJobRepository:
    def __init__(self, engine):
        self.engine = engine

    def create(self, job: PrintJob) -> PrintJob:
        with Session(self.engine) as session:
            session.add(job)
            session.commit()
            session.refresh(job)
            return job

    def get_by_id(self, job_id: int) -> Optional[PrintJob]:
        with Session(self.engine) as session:
            return session.get(PrintJob, job_id)
