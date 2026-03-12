from pydantic import BaseModel
from typing import List

class TestPrinterJobResponseDTO(BaseModel):
    id: int
    channel: int
    template: str
    status: str

class TestPrinterResponseDTO(BaseModel):
    printer: str
    jobs: List[TestPrinterJobResponseDTO]
