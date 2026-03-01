import pytest
from fastapi import status
from infrastructure.repositories.channel_repository import ChannelRepository
from infrastructure.repositories.template_repository import TemplateRepository
from infrastructure.db.database import engine

def test_preview_label_success(client):
    # Setup: Create template and channel
    template_repo = TemplateRepository(engine)
    channel_repo = ChannelRepository(engine)
    
    # Use existing template file with prefix
    template = template_repo.create(name="Zebra Label", file_path="labels/zebra_label.zpl")
    channel_repo.create(channel_number=3, description="Channel for Labels", template_id=template.id)
    
    payload = {
        "channel": 3,
        "client_code": "TEST_LBL",
        "client_name": "Test Label Client",
        "extra_data": '{"to": "John Doe", "address": "Main St 123", "city": "Springfield", "packages": "1"}'
    }
    
    response = client.post("/templates/label/preview", json=payload)
    
    assert response.status_code == status.HTTP_200_OK
    # API returns application/vnd.zpl for labels
    assert response.headers["content-type"] == "application/vnd.zpl"
    # ZPL starts with ^XA
    assert b"^XA" in response.content

def test_preview_label_wrong_template_type(client):
    # Setup: Create a channel with HTML template
    template_repo = TemplateRepository(engine)
    channel_repo = ChannelRepository(engine)
    
    template = template_repo.create(name="Remito HTML", file_path="remitos/base_remito.html")
    channel_repo.create(channel_number=3, description="Channel for Label", template_id=template.id)
    
    payload = {
        "channel": 3,
        "client_code": "TEST_ERR"
    }
    
    response = client.post("/templates/label/preview", json=payload)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "no está configurado con una plantilla de etiquetas" in response.json()["detail"]

def test_preview_label_channel_not_found(client):
    payload = {
        "channel": 999,
        "client_code": "TEST_NONE"
    }
    
    response = client.post("/templates/label/preview", json=payload)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "no existe" in response.json()["detail"]
