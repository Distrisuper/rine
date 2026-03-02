import pytest
from fastapi import status
from infrastructure.repositories.channel_repository import ChannelRepository
from infrastructure.repositories.template_repository import TemplateRepository
from infrastructure.db.database import engine

def test_preview_label_success(client):
    # Setup: Create template and channel
    template_repo = TemplateRepository(engine)
    channel_repo = ChannelRepository(engine)
    
    # Usamos el path real que existe en el proyecto
    template = template_repo.create(name="Zebra Label", file_path="labels/zebra_label.zpl")
    channel_repo.create(channel_number=3, description="Channel for Labels", template_id=template.id)
    
    # Parámetros por Query String
    params = {
        "to": "John Doe",
        "address": "Main St 123",
        "city": "Springfield",
        "packages": "1"
    }
    
    response = client.get("/templates/preview/label/3", params=params)
    
    assert response.status_code == status.HTTP_200_OK
    # API returns application/vnd.zpl for labels
    assert response.headers["content-type"] == "application/vnd.zpl"
    # ZPL content
    assert b"^XA" in response.content

def test_preview_label_wrong_template_type(client):
    # Setup: Create a channel with HTML template
    template_repo = TemplateRepository(engine)
    channel_repo = ChannelRepository(engine)
    
    template = template_repo.create(name="Remito HTML", file_path="remitos/base_remito.html")
    channel_repo.create(channel_number=3, description="Channel for Label", template_id=template.id)
    
    response = client.get("/templates/preview/label/3")
    
    # El caso de uso lanza ValueError si el template no termina en .zpl
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "no está configurado con una plantilla de etiquetas" in response.json()["detail"]

def test_preview_label_channel_not_found(client):
    response = client.get("/templates/preview/label/999")
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "no existe" in response.json()["detail"]
