import pytest
from fastapi import status
from sqlmodel import Session, select
from domain.entities.print_job import PrintJob
from infrastructure.db.database import engine

def test_create_print_job_success(client):
    payload = {
        "channel": 1,
        "client_code": "CL001",
        "client_name": "Cliente de Prueba E2E",
        "payload": {
            "order_number": 12345,
            "items": [{"sku": "PROD1", "qty": 2}]
        }
    }
    
    response = client.post("/print-jobs", json=payload)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # Validar campos básicos de respuesta
    assert data["client_code"] == "CL001"
    assert data["status"] == "pending"
    assert data["channel"] == 1
    assert "id" in data
    assert "date_created" in data

    # Verificar persistencia real en la DB
    with Session(engine) as session:
        job = session.get(PrintJob, data["id"])
        assert job is not None
        assert job.client_name == "Cliente de Prueba E2E"
        assert job.status == "pending"

def test_create_print_job_validation_error(client):
    # Payload inválido: falta client_code y payload
    payload = {
        "channel": 1,
        "client_name": "Incompleto"
    }
    
    response = client.post("/print-jobs", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
