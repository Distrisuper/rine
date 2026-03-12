from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class Template(SQLModel, table=True):
    __tablename__ = "templates"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    file_path: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
