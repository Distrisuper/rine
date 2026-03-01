from pydantic import BaseModel

class HelloGetResponseDTO(BaseModel):
    message: str
