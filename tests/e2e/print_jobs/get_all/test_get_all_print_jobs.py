import pytest
from fastapi import status
from datetime import datetime, timedelta
from infrastructure.repositories.print_job_repository import PrintJobRepository
from domain.entities.print_job import PrintJob
from infrastructure.db.database import engine

def test_list_print_jobs_empty(client):
    response = client.get("/print-jobs")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["data"] == []
    assert data["total"] == 0
    assert data["page"] == 1

def test_list_print_jobs_pagination_and_filters(client):
    repo = PrintJobRepository(engine)
    
    # Setup: Crear 3 trabajos con diferentes estados e impresoras
    j1 = PrintJob(client_code="C1", client_name="N1", channel=1, status="pending", number_of_copies=1, attempt_count=0, payload="{}", date_created=datetime.utcnow())
    j2 = PrintJob(client_code="C2", client_name="N2", channel=2, status="sent", number_of_copies=2, attempt_count=0, printer_name="Zebra1", payload="{}", date_created=datetime.utcnow() - timedelta(hours=1))
    j3 = PrintJob(client_code="C3", client_name="N3", channel=1, status="failed", number_of_copies=3, attempt_count=1, payload="{}", date_created=datetime.utcnow() - timedelta(days=1))
    
    repo.create(j1)
    repo.create(j2)
    repo.create(j3)
    
    # 1. Probar listado total
    response = client.get("/print-jobs")
    assert response.json()["total"] == 3
    
    # 2. Probar filtro por estado
    response = client.get("/print-jobs?status=sent")
    data = response.json()
    assert data["total"] == 1
    assert data["data"][0]["client_code"] == "C2"
    assert data["data"][0]["number_of_copies"] == 2
    assert data["data"][0]["attempt_count"] == 0
    
    # 3. Probar filtro por impresora
    response = client.get("/print-jobs?printer_name=Zebra1")
    assert response.json()["total"] == 1
    
    # 4. Probar paginación
    response = client.get("/print-jobs?limit=2&page=1")
    data = response.json()
    assert len(data["data"]) == 2
    assert data["total"] == 3
    
    # 5. Probar filtro de fecha (desde hace 2 horas hasta ahora)
    date_from = (datetime.utcnow() - timedelta(hours=2)).isoformat()
    response = client.get(f"/print-jobs?date_from={date_from}")
    assert response.json()["total"] == 2 # j1 y j2

def test_list_print_jobs_includes_copies_and_attempts(client):
    """Verificar que la respuesta incluye number_of_copies y attempt_count"""
    repo = PrintJobRepository(engine)
    
    # Setup: Crear un job con parámetros específicos
    job = PrintJob(
        client_code="TEST",
        client_name="Test Job",
        channel=1,
        status="pending",
        number_of_copies=5,
        attempt_count=2,
        payload="{}",
        date_created=datetime.utcnow()
    )
    repo.create(job)
    
    # Obtener listado
    response = client.get("/print-jobs")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert len(data["data"]) > 0
    
    # Buscar nuestro job
    test_job = next((j for j in data["data"] if j["client_code"] == "TEST"), None)
    assert test_job is not None
    
    # Validar campos críticos
    assert test_job["number_of_copies"] == 5
    assert test_job["attempt_count"] == 2
    assert "id" in test_job
    assert "status" in test_job
    assert "date_created" in test_job
