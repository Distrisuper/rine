from dataclasses import dataclass
from typing import Optional


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
        from domain.entities.document_type import get_printer_key
        printer_key = get_printer_key(channel)
        return cls.get_printer(printer_key)
