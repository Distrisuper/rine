import pytest
from fastapi import status
from infrastructure.repositories.channel_repository import ChannelRepository
from infrastructure.db.database import engine

def test_delete_channel_success(client):
    # Setup: Crear un canal
    channel_repo = ChannelRepository(engine)
    channel = channel_repo.create(channel_number=1, description="A eliminar")
    
    response = client.delete(f"/channels/{channel.id}")
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "deleted"
    assert response.json()["id"] == channel.id
    
    # Verificar que ya no existe
    assert channel_repo.get_by_id(channel.id) is None

def test_delete_channel_not_found(client):
    response = client.delete("/channels/9999")
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "no encontrado" in response.json()["detail"].lower()
