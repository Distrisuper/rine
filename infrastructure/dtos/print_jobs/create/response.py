from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Union


class CreatePrintJobResponseDTO(BaseModel):
    id: int
    client_code: str
    client_name: str
    channel: int
    status: str
    print_count: int
    print_type: Optional[str] = None
    date_created: Union[datetime, str]
    date_started: Optional[Union[datetime, str]] = None
    date_processed: Optional[Union[datetime, str]] = None
    printer_name: Optional[str] = None
    error_message: Optional[str] = None
