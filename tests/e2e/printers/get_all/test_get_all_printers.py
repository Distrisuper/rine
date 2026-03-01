import pytest
from fastapi import status
from infrastructure.repositories.printer_repository import PrinterRepository
from infrastructure.repositories.channel_repository import ChannelRepository
from infrastructure.db.database import engine

def test_get_all_printers_empty(client):
    response = client.get("/printers")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []

def test_get_all_printers_with_data(client):
    # Setup: Crear una impresora con canales
    printer_repo = PrinterRepository(engine)
    channel_repo = ChannelRepository(engine)
    
    c1 = channel_repo.create(channel_number=10, description="Canal 10")
    printer_repo.create_printer(name="Printer List Test", channel_ids=[c1.id])
    
    response = client.get("/printers")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Printer List Test"
    assert len(data[0]["channels"]) == 1
    assert data[0]["channels"][0]["channel_number"] == 10
