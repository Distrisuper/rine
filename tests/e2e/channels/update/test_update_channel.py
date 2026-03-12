import pytest
from fastapi import status
from infrastructure.repositories.channel_repository import ChannelRepository
from infrastructure.repositories.template_repository import TemplateRepository
from infrastructure.db.database import engine

def test_update_channel_success(client):
    # Setup: Crear un canal
    channel_repo = ChannelRepository(engine)
    channel = channel_repo.create(channel_number=1, description="Original", document_source="INTERNAL")
    
    payload = {
        "description": "Actualizado",
        "is_active": False,
        "template_id": None,
        "document_source": "S3_REMITOS_FRIC_ROT"
    }
    
    response = client.put(f"/channels/{channel.id}", json=payload)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["description"] == "Actualizado"
    assert data["is_active"] is False
    assert data["document_source"] == "S3_REMITOS_FRIC_ROT"
    assert data["id"] == channel.id

def test_update_channel_not_found(client):
    payload = {
        "description": "No existo"
    }
    response = client.put("/channels/9999", json=payload)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "no encontrado" in response.json()["detail"].lower()

def test_update_channel_invalid_source_error(client):
    # Setup: Crear un canal
    channel_repo = ChannelRepository(engine)
    channel = channel_repo.create(channel_number=500, description="Original", document_source="INTERNAL")
    
    payload = {
        "document_source": "INVALID_SOURCE"
    }
    
    response = client.put(f"/channels/{channel.id}", json=payload)
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
