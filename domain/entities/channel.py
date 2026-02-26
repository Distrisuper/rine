from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class Channel(SQLModel, table=True):
    __tablename__ = "channels"

    id: Optional[int] = Field(default=None, primary_key=True)
    channel_number: int = Field(unique=True)
    description: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
