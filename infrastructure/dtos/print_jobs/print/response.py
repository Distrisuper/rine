from pydantic import BaseModel


class PrintJobResponseDTO(BaseModel):
    printer: str
    job_id: int
