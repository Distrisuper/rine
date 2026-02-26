from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class Printer(SQLModel, table=True):
    __tablename__ = "printers"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    printer_type: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PrinterChannel(SQLModel, table=True):
    __tablename__ = "printer_channels"

    printer_id: int = Field(foreign_key="printers.id", primary_key=True)
    channel: int = Field(primary_key=True)
    channel_id: Optional[int] = Field(foreign_key="channels.id", default=None)
    description: Optional[str] = None
    is_active: bool = True
