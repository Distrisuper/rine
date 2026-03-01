import pytest
from fastapi import status
from infrastructure.repositories.channel_repository import ChannelRepository
from infrastructure.repositories.template_repository import TemplateRepository
from infrastructure.db.database import engine

def test_preview_remito_success(client):
    # Setup: Create template and channel
    template_repo = TemplateRepository(engine)
    channel_repo = ChannelRepository(engine)
    
    # Use existing template file with prefix
    template = template_repo.create(name="Base Remito", file_path="remitos/base_remito.html")
    channel_repo.create(channel_number=4, description="Channel for Remitos", template_id=template.id)
    
    # Extra data for remito needs to be a JSON string that RemitoRenderData can parse
    extra_data = {
        "remito_id": "R-0001",
        "fecha": "01/03/2026",
        "reparto": "R1",
        "sucursal": "S1",
        "items": [
            {"codigo": "P1", "cantidad": 10, "descripcion": "Product 1"}
        ],
        "total": 1500.50
    }
    
    payload = {
        "channel": 4,
        "client_code": "TEST_REM",
        "client_name": "Test Remito Client",
        "extra_data": str(extra_data).replace("'", '"') # Ensure valid JSON string
    }
    
    response = client.post("/templates/remito/preview", json=payload)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"] == "application/pdf"
    # PDF magic number is %PDF
    assert response.content.startswith(b"%PDF")

def test_preview_remito_wrong_template_type(client):
    # Setup: Create a channel with ZPL template
    template_repo = TemplateRepository(engine)
    channel_repo = ChannelRepository(engine)
    
    template = template_repo.create(name="Zebra ZPL", file_path="labels/zebra_label.zpl")
    # Use channel 4 (allowed by resolver) but associate a ZPL template
    channel_repo.create(channel_number=4, description="Channel for ZPL", template_id=template.id)
    
    payload = {
        "channel": 4,
        "client_code": "TEST_ERR"
    }
    
    response = client.post("/templates/remito/preview", json=payload)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "no está configurado con una plantilla de remitos" in response.json()["detail"]
