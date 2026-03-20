from pydantic import BaseModel


class AdminUnlockResponseDTO(BaseModel):
    unlocked: bool
