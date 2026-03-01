from sqlmodel import Session, select, and_, desc, func
from datetime import datetime
from typing import List, Optional, Tuple
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

    def get_all(
        self,
        printer_name: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 100
    ) -> Tuple[List[PrintJob], int]:
        with Session(self.engine) as session:
            query = select(PrintJob)

            filters = []
            if printer_name:
                filters.append(PrintJob.printer_name == printer_name)
            if date_from:
                filters.append(PrintJob.date_created >= date_from)
            if date_to:
                filters.append(PrintJob.date_created <= date_to)
            if status:
                filters.append(PrintJob.status == status)

            if filters:
                query = query.where(and_(*filters))

            # Obtener el total antes de paginar
            total_query = select(func.count()).select_from(query.subquery())
            total = session.exec(total_query).one()

            # Aplicar orden y paginación
            query = query.order_by(desc(PrintJob.date_created))
            query = query.offset((page - 1) * limit).limit(limit)
            
            jobs = session.exec(query).all()
            return list(jobs), total
