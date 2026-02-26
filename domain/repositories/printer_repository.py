from sqlmodel import Session, select
from typing import Optional

from domain.entities.printer import Printer, PrinterChannel


class PrinterRepository:
    def __init__(self, engine):
        self.engine = engine

    def get_printer_for_channel(self, channel: int) -> Optional[Printer]:
        with Session(self.engine) as session:
            statement = (
                select(Printer)
                .join(PrinterChannel, Printer.id == PrinterChannel.printer_id)
                .where(PrinterChannel.channel == channel)
                .where(PrinterChannel.is_active == True)
                .where(Printer.is_active == True)
            )
            return session.exec(statement).first()

    def get_all_printers(self) -> list[Printer]:
        with Session(self.engine) as session:
            return list(session.exec(select(Printer)).all())

    def create_printer(self, name: str, printer_type: str) -> Printer:
        with Session(self.engine) as session:
            printer = Printer(name=name, printer_type=printer_type)
            session.add(printer)
            session.commit()
            session.refresh(printer)
            return printer

    def add_channel_to_printer(
        self, printer_id: int, channel: int, description: str = None
    ) -> PrinterChannel:
        with Session(self.engine) as session:
            pc = PrinterChannel(
                printer_id=printer_id,
                channel=channel,
                description=description,
            )
            session.add(pc)
            session.commit()
            return pc

    def get_all_channels_with_printers(self) -> list[dict]:
        with Session(self.engine) as session:
            statement = (
                select(Printer, PrinterChannel)
                .join(PrinterChannel, Printer.id == PrinterChannel.printer_id)
            )
            results = session.exec(statement).all()
            return [
                {
                    "printer_id": p.id,
                    "printer_name": p.name,
                    "printer_type": p.printer_type,
                    "printer_is_active": p.is_active,
                    "channel": pc.channel,
                    "description": pc.description,
                    "channel_is_active": pc.is_active,
                }
                for p, pc in results
            ]

    def delete_printer(self, printer_id: int) -> bool:
        with Session(self.engine) as session:
            printer = session.get(Printer, printer_id)
            if printer:
                session.delete(printer)
                session.commit()
                return True
            return False
