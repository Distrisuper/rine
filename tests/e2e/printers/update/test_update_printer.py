import pytest
from fastapi import status
from infrastructure.repositories.printer_repository import PrinterRepository
from infrastructure.repositories.channel_repository import ChannelRepository
from infrastructure.db.database import engine

def test_update_printer_basic_info(client):
    # Setup: Crear una impresora
    printer_repo = PrinterRepository(engine)
    printer_data = printer_repo.create_printer(name="Old Name")
    printer_id = printer_data["id"]
    
    payload = {
        "name": "New Name",
        "is_active": False
    }
    
    response = client.put(f"/printers/{printer_id}", json=payload)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "New Name"
    assert data["is_active"] is False

def test_update_printer_channels(client):
    # Setup: Crear una impresora con un canal, y tener otro canal listo
    printer_repo = PrinterRepository(engine)
    channel_repo = ChannelRepository(engine)
    
    c1 = channel_repo.create(channel_number=1, description="Canal 1")
    c2 = channel_repo.create(channel_number=2, description="Canal 2")
    
    printer_data = printer_repo.create_printer(name="Printer Channels Test", channel_ids=[c1.id])
    printer_id = printer_data["id"]
    
    # Actualizar para que SOLO tenga el canal 2
    payload = {
        "channel_ids": [c2.id]
    }
    
    response = client.put(f"/printers/{printer_id}", json=payload)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["channels"]) == 1
    assert data["channels"][0]["channel_number"] == 2

def test_update_printer_not_found(client):
    payload = {"name": "No existo"}
    response = client.put("/printers/9999", json=payload)
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "no encontrada" in response.json()["detail"].lower()
