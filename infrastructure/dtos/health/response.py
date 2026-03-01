from pydantic import BaseModel

class HealthResponseDTO(BaseModel):
    status: str
