from dataclasses import dataclass
from typing import Optional

from infrastructure.db.database import engine
from sqlmodel import Session, select
from domain.entities.printer import Printer, PrinterChannel
from domain.entities.channel import Channel


@dataclass
class PrinterConfig:
    name: str
    is_active: bool
    printer_type: str


class PrinterRegistry:
    PRINTERS = {
        "zebra_printer": PrinterConfig(
            name="Zebra_ZD420",
            is_active=True,
            printer_type="zebra"
        ),
        "laser_printer": PrinterConfig(
            name="HP_LaserJet",
            is_active=True,
            printer_type="laser"
        ),
    }

    @classmethod
    def get_printer(cls, printer_key: str) -> PrinterConfig:
        if printer_key not in cls.PRINTERS:
            raise ValueError(f"Printer key '{printer_key}' no configurado")
        return cls.PRINTERS[printer_key]

    @classmethod
    def get_printer_for_channel(cls, channel: int) -> PrinterConfig:
        with Session(engine) as session:
            printer_channel = (
                select(PrinterChannel)
                .join(Channel, PrinterChannel.channel_id == Channel.id)
                .where(Channel.channel_number == channel)
                .where(PrinterChannel.is_active == True)
            ).first()

            if not printer_channel:
                raise ValueError(f"No hay impresora configurada para channel {channel}")

            printer = session.get(Printer, printer_channel.printer_id)
            if not printer or not printer.is_active:
                raise ValueError(f"Impresora no encontrada o inactiva para channel {channel}")

            # Map printer name to printer_type
            if "zebra" in printer.name.lower():
                printer_type = "zebra_printer"
            else:
                printer_type = "laser_printer"

            return PrinterConfig(
                name=printer.name,
                is_active=printer.is_active,
                printer_type=printer_type
            )
