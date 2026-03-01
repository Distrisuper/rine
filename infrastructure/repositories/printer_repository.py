from sqlmodel import Session, select
from typing import Optional

from domain.entities.printer import Printer, PrinterChannel
from domain.entities.channel import Channel
from domain.value_objects import PrinterConfig
from domain.repositories.printer_repository_interface import PrinterRepositoryInterface


class PrinterRepository(PrinterRepositoryInterface):
    def __init__(self, engine):
        self.engine = engine

    def get_printer_for_channel(self, channel: int) -> Optional[PrinterConfig]:
        with Session(self.engine) as session:
            statement = (
                select(Printer, PrinterChannel)
                .join(PrinterChannel, Printer.id == PrinterChannel.printer_id)
                .join(Channel, PrinterChannel.channel_id == Channel.id)
                .where(Channel.channel_number == channel)
                .where(PrinterChannel.is_active == True)
                .where(Printer.is_active == True)
            )
            result = session.exec(statement).first()
            
            if not result:
                return None
                
            printer, pc = result
            
            # Lógica de mapeo de tipo movida desde el antiguo Registry
            printer_type = "laser_printer"
            if "zebra" in printer.name.lower():
                printer_type = "zebra_printer"
                
            return PrinterConfig(
                name=printer.name,
                is_active=printer.is_active,
                printer_type=printer_type
            )

    def get_all_printers(self) -> list[Printer]:
        with Session(self.engine) as session:
            return list(session.exec(select(Printer)).all())

    def get_printer_by_id(self, printer_id: int) -> Optional[Printer]:
        with Session(self.engine) as session:
            return session.get(Printer, printer_id)

    def create_printer(self, name: str, channel_ids: list[int] = []) -> dict:
        with Session(self.engine) as session:
            printer = Printer(name=name)
            session.add(printer)
            session.commit()
            session.refresh(printer)
            printer_id = printer.id
            printer_name = printer.name
            
            if channel_ids:
                for ch_id in channel_ids:
                    channel = session.get(Channel, ch_id)
                    if channel:
                        pc = PrinterChannel(
                            printer_id=printer_id,
                            channel=channel.channel_number,
                            channel_id=ch_id,
                            description=channel.description,
                        )
                        session.add(pc)
                session.commit()
            
            return {
                "id": printer_id,
                "name": printer_name,
                "channels": self.get_printer_channels(printer_id) if printer_id > 0 else [],
            }

    def update_printer(self, printer_id: int, name: str = '', is_active: Optional[bool] = None) -> Optional[dict]:
        with Session(self.engine) as session:
            printer = session.get(Printer, printer_id)
            if not printer:
                return None
            
            if name is not None and name != '':
                printer.name = name
            if is_active is not None:
                printer.is_active = is_active
            
            session.commit()
            
            return {
                "id": printer.id,
                "name": printer.name,
                "is_active": printer.is_active,
                "channels": self.get_printer_channels(printer_id) if printer_id > 0 else [],
            }

    def set_printer_channels(self, printer_id: int, channel_ids: list[int]) -> bool:
        with Session(self.engine) as session:
            printer = session.get(Printer, printer_id)
            if not printer:
                return False
            
            existing_pcs = session.exec(
                select(PrinterChannel).where(PrinterChannel.printer_id == printer_id)
            ).all()
            for pc in existing_pcs:
                session.delete(pc)
            
            for ch_id in channel_ids:
                channel = session.get(Channel, ch_id)
                if channel:
                    pc = PrinterChannel(
                        printer_id=printer_id,
                        channel=channel.channel_number,
                        channel_id=ch_id,
                        description=channel.description,
                    )
                    session.add(pc)
            
            session.commit()
            return True

    def get_printer_channels(self, printer_id: int) -> list[dict]:
        if printer_id <= 0:
            raise ValueError("printer_id debe ser un entero positivo")
        with Session(self.engine) as session:
            statement = (
                select(PrinterChannel, Channel)
                .join(Channel, PrinterChannel.channel_id == Channel.id)
                .where(PrinterChannel.printer_id == printer_id)
            )
            results = session.exec(statement).all()
            return [
                {
                    "channel_id": ch.id,
                    "channel_number": pc.channel,
                    "description": ch.description,
                    "is_active": pc.is_active,
                }
                for pc, ch in results
            ]

    def get_all_printers_with_channels(self) -> list[dict]:
        with Session(self.engine) as session:
            printers = session.exec(select(Printer)).all()
            
            result = []
            for p in printers:
                channels = self.get_printer_channels(p.id)
                result.append({
                    "id": p.id,
                    "name": p.name,
                    "is_active": p.is_active,
                    "channels": channels,
                    "channel_count": len(channels),
                })
            
            return result

    def get_all_channels_with_printers(self) -> list[dict]:
        with Session(self.engine) as session:
            statement = (
                select(Printer, PrinterChannel, Channel)
                .join(PrinterChannel, Printer.id == PrinterChannel.printer_id)
                .join(Channel, PrinterChannel.channel_id == Channel.id)
            )
            results = session.exec(statement).all()
            return [
                {
                    "printer_id": p.id,
                    "printer_name": p.name,
                    "printer_is_active": p.is_active,
                    "channel": pc.channel,
                    "description": ch.description,
                    "channel_is_active": pc.is_active,
                }
                for p, pc, ch in results
            ]

    def delete_printer(self, printer_id: int) -> bool:
        with Session(self.engine) as session:
            printer = session.get(Printer, printer_id)
            if printer:
                pcs = session.exec(
                    select(PrinterChannel).where(PrinterChannel.printer_id == printer_id)
                ).all()
                for pc in pcs:
                    session.delete(pc)
                
                session.delete(printer)
                session.commit()
                return True
            return False
