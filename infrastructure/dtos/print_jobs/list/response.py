from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class PrintJobResponseDTO(BaseModel):
    id: int
    client_code: str
    client_name: str
    channel: int
    status: str
    number_of_copies: int
    attempt_count: int = 0
    print_type: Optional[str] = None
    date_created: Optional[datetime] = None
    date_started: Optional[datetime] = None
    date_processed: Optional[datetime] = None
    printer_name: Optional[str] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True

class PaginatedPrintJobsResponseDTO(BaseModel):
    data: List[PrintJobResponseDTO]
    page: int
    limit: int
    total: int
