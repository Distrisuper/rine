import pytest
from fastapi import status
from infrastructure.repositories.channel_repository import ChannelRepository
from infrastructure.db.database import engine

def test_create_printer_simple_success(client):
    payload = {
        "name": "HP Laserjet 1020",
        "channel_ids": []
    }
    
    response = client.post("/printers", json=payload)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "HP Laserjet 1020"
    assert "id" in data
    assert data["channels"] == []

def test_create_printer_with_channels_success(client):
    # Setup: Crear canales previos
    channel_repo = ChannelRepository(engine)
    c1 = channel_repo.create(channel_number=1, description="Canal 1")
    c2 = channel_repo.create(channel_number=2, description="Canal 2")
    
    payload = {
        "name": "Zebra ZT230",
        "channel_ids": [c1.id, c2.id]
    }
    
    response = client.post("/printers", json=payload)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Zebra ZT230"
    assert len(data["channels"]) == 2
    
    # Verificar que los canales devueltos coincidan
    channel_numbers = [ch["channel_number"] for ch in data["channels"]]
    assert 1 in channel_numbers
    assert 2 in channel_numbers

def test_create_printer_validation_error(client):
    # Payload sin nombre
    payload = {
        "channel_ids": []
    }
    
    response = client.post("/printers", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
