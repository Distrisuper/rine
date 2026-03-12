import pytest
import json
from fastapi import status
from infrastructure.repositories.channel_repository import ChannelRepository
from infrastructure.repositories.template_repository import TemplateRepository
from infrastructure.db.database import engine

def test_preview_remito_success(client):
    # Setup: Create template and channel
    template_repo = TemplateRepository(engine)
    channel_repo = ChannelRepository(engine)
    
    # Usamos el path real que existe en el proyecto
    template = template_repo.create(name="Base Remito", file_path="remitos/base_remito.html")
    channel_repo.create(channel_number=4, description="Channel for Remitos", template_id=template.id, document_source="INTERNAL")
    
    # Datos en el Body (POST)
    items = [
        {"codigo": "P1", "cantidad": 10, "descripcion": "Product 1"}
    ]
    
    payload = {
        "channel": 4,
        "client_code": "TEST_REM",
        "client_name": "Test Remito Client",
        "payload": {
            "order_number": 12345,
            "address": "Calle Falsa 123",
            "city": "CABA",
            "items": items,
            "total": 1500.50,
            "remito_id": "R-0001",
            "fecha": "01/03/2026"
        }
    }
    
    response = client.post("/templates/preview/remito/4", json=payload)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"] == "application/pdf"
    # PDF magic number is %PDF
    assert response.content.startswith(b"%PDF")

def test_preview_remito_wrong_template_type(client):
    # Setup: Create a channel with ZPL template
    template_repo = TemplateRepository(engine)
    channel_repo = ChannelRepository(engine)
    
    template = template_repo.create(name="Zebra ZPL", file_path="labels/zebra_label.zpl")
    # Asociamos un ZPL a un canal de remito
    channel_repo.create(channel_number=4, description="Channel for ZPL", template_id=template.id, document_source="INTERNAL")
    
    payload = {
        "channel": 4,
        "client_code": "TEST",
        "client_name": "Test Client",
        "payload": {}
    }
    
    response = client.post("/templates/preview/remito/4", json=payload)
    
    # El caso de uso lanza ValueError si el template no termina en .html
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "no está configurado con una plantilla de remitos" in response.json()["detail"]
