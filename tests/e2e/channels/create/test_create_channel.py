import pytest
from fastapi import status
from infrastructure.repositories.template_repository import TemplateRepository
from infrastructure.db.database import engine

def test_create_channel_success(client):
    # Setup: Necesitamos un template para asociar al canal
    template_repo = TemplateRepository(engine)
    template = template_repo.create(name="Test Template", file_path="test.html")
    
    payload = {
        "channel_number": 100,
        "description": "Canal de Prueba E2E",
        "template_id": template.id
    }
    
    response = client.post("/channels", json=payload)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["channel_number"] == 100
    assert data["description"] == "Canal de Prueba E2E"
    assert data["template_id"] == template.id
    assert "id" in data


def test_create_channel_without_template(client):
    """Channel sin template (ej. channel 2 para PDF pre-generados)."""
    payload = {
        "channel_number": 2,
        "description": "PDF pre-generados (GM)",
        "template_id": None
    }
    
    response = client.post("/channels", json=payload)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["channel_number"] == 2
    assert data["description"] == "PDF pre-generados (GM)"
    assert data["template_id"] is None

def test_create_channel_duplicate_error(client):
    # Setup: Crear un template y un canal primero
    template_repo = TemplateRepository(engine)
    template = template_repo.create(name="Test Template", file_path="test.html")
    
    payload = {
        "channel_number": 200,
        "description": "Primer Canal",
        "template_id": template.id
    }
    client.post("/channels", json=payload)
    
    # Intentar crear otro con el mismo número
    response = client.post("/channels", json=payload)
    
    # El Global Error Handler traduce ValueError a 400
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "ya existe" in response.json()["detail"]

def test_create_channel_validation_error(client):
    # Payload inválido (falta channel_number)
    payload = {
        "description": "Sin número",
        "template_id": 1
    }
    
    response = client.post("/channels", json=payload)
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
