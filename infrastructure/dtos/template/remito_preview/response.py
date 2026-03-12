from pydantic import BaseModel


class RemitoPreviewResponseDTO(BaseModel):
    content_type: str
    size: int
    content_base64: str
