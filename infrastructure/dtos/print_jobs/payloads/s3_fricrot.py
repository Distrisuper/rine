from pydantic import BaseModel, field_validator, model_validator
from typing import Optional, Any

class S3FricRotPayloadDTO(BaseModel):
    pdf_base64: Optional[str] = None
    pdf_url: Optional[str] = None
    ftp_filename: Optional[str] = None
    pdf_path: Optional[str] = None
    extra_data: Optional[dict[str, Any]] = None

    @model_validator(mode='after')
    def require_one_source(self):
        sources = [self.pdf_base64, self.pdf_url, self.ftp_filename, self.pdf_path]
        if not any(sources):
            raise ValueError("Debe proporcionar al menos una fuente de PDF: pdf_base64, pdf_url, ftp_filename o pdf_path")
        return self
