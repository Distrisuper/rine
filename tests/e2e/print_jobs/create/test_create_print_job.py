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


def test_create_job_copies_zero(client):
    """number_of_copies = 0 debe ser rechazado (mínimo 1)"""
    payload = {
        "channel": 1,
        "client_code": "CL001",
        "client_name": "Cliente Test",
        "payload": {"order_number": 123},
        "number_of_copies": 0
    }
    
    response = client.post("/print-jobs", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_job_copies_negative(client):
    """number_of_copies negativo debe ser rechazado"""
    payload = {
        "channel": 1,
        "client_code": "CL001",
        "client_name": "Cliente Test",
        "payload": {"order_number": 123},
        "number_of_copies": -5
    }
    
    response = client.post("/print-jobs", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_job_copies_over_100(client):
    """number_of_copies > 100 debe ser rechazado"""
    payload = {
        "channel": 1,
        "client_code": "CL001",
        "client_name": "Cliente Test",
        "payload": {"order_number": 123},
        "number_of_copies": 101
    }
    
    response = client.post("/print-jobs", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_job_copies_string(client):
    """number_of_copies como string debe ser rechazado"""
    payload = {
        "channel": 1,
        "client_code": "CL001",
        "client_name": "Cliente Test",
        "payload": {"order_number": 123},
        "number_of_copies": "abc"
    }
    
    response = client.post("/print-jobs", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_job_copies_valid(client):
    """number_of_copies válido (50) debe ser aceptado"""
    payload = {
        "channel": 1,
        "client_code": "CL001",
        "client_name": "Cliente Test",
        "payload": {"order_number": 123},
        "number_of_copies": 50
    }
    
    response = client.post("/print-jobs", json=payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["number_of_copies"] == 50


def test_create_job_default_copies(client):
    """Sin number_of_copies debe usar default=1"""
    payload = {
        "channel": 1,
        "client_code": "CL001",
        "client_name": "Cliente Test",
        "payload": {"order_number": 123}
    }
    
    response = client.post("/print-jobs", json=payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["number_of_copies"] == 1
