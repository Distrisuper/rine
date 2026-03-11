from sqlmodel import SQLModel, Field, Session
from datetime import datetime
from typing import Optional
from domain.entities.template import Template


class Channel(SQLModel, table=True):
    __tablename__ = "channels"

    id: Optional[int] = Field(default=None, primary_key=True)
    channel_number: int = Field(unique=True)
    description: Optional[str] = None
    is_active: bool = True
    template_id: Optional[int] = Field(foreign_key="templates.id", default=None)
    document_source: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    def get_template(self, session: Session) -> Optional[Template]:
        if not self.template_id:
            return None
        return session.get(Template, self.template_id)
