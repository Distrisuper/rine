from pydantic import BaseModel


class GetOneStatusByNameRequestDTO(BaseModel):
    name: str
