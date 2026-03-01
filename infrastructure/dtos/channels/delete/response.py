from pydantic import BaseModel

class DeleteChannelResponseDTO(BaseModel):
    status: str
    id: int
