import pytest
from fastapi import status
from sqlmodel import Session, select
from infrastructure.repositories.printer_repository import PrinterRepository
from infrastructure.repositories.channel_repository import ChannelRepository
from domain.entities.printer import Printer, PrinterChannel
from infrastructure.db.database import engine

def test_delete_printer_success(client):
    # Setup: Crear una impresora con canales
    printer_repo = PrinterRepository(engine)
    channel_repo = ChannelRepository(engine)
    c1 = channel_repo.create(channel_number=5, description="Canal 5")
    printer_data = printer_repo.create_printer(name="To be deleted", channel_ids=[c1.id])
    printer_id = printer_data["id"]
    
    response = client.delete(f"/printers/{printer_id}")
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verificar en DB que no existe la impresora
    with Session(engine) as session:
        p = session.get(Printer, printer_id)
        assert p is None
        
        # Verificar que se borraron las asociaciones (Cascade delete manual en el repo)
        pcs = session.exec(select(PrinterChannel).where(PrinterChannel.printer_id == printer_id)).all()
        assert len(pcs) == 0

def test_delete_printer_not_found(client):
    response = client.delete("/printers/9999")
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "no encontrada" in response.json()["detail"].lower()
