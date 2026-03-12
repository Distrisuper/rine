import pytest
from fastapi import status
from infrastructure.repositories.channel_repository import ChannelRepository
from infrastructure.repositories.template_repository import TemplateRepository
from infrastructure.db.database import engine

def test_list_channels_empty(client):
    response = client.get("/channels")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []

def test_list_channels_with_data(client):
    # Setup: Crear un template y un canal
    template_repo = TemplateRepository(engine)
    channel_repo = ChannelRepository(engine)
    
    template = template_repo.create(name="T1", file_path="t1.html")
    channel_repo.create(channel_number=1, description="C1", template_id=template.id, document_source="INTERNAL")
    channel_repo.create(channel_number=2, description="C2", template_id=None, document_source="S3_REMITOS_FRIC_ROT")
    
    response = client.get("/channels")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    
    # Verificar orden (por channel_number según el repo)
    assert data[0]["channel_number"] == 1
    assert data[0]["template_name"] == "T1"
    assert data[0]["document_source"] == "INTERNAL"
    
    assert data[1]["channel_number"] == 2
    assert data[1]["template_name"] is None
    assert data[1]["document_source"] == "S3_REMITOS_FRIC_ROT"
