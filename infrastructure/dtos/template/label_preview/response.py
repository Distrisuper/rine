from pydantic import BaseModel


class LabelPreviewResponseDTO(BaseModel):
    content_type: str
    size: int
    content_base64: str
