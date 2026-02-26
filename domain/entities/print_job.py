from sqlmodel import SQLModel, Field, Index
from datetime import datetime
from typing import Optional


class PrintJob(SQLModel, table=True):
    __tablename__ = "print_jobs"
    __table_args__ = (
        Index("idx_print_jobs_status_created", "status", "date_created"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    client_id: Optional[str] = Field(default=None)
    client_code: str
    client_name: str
    print_type: str
    status: str = "pending"
    print_count: int = 0
    host: Optional[int] = None
    date_created: datetime = Field(default_factory=datetime.utcnow)
    date_started: Optional[datetime] = None
    date_processed: Optional[datetime] = None
    payload: str  # JSON
    printer_name: Optional[str] = None
    error_message: Optional[str] = None
