import pytest
from fastapi import status
from sqlmodel import Session, select
from domain.entities.print_job import PrintJob
from infrastructure.db.database import engine
from infrastructure.repositories.channel_repository import ChannelRepository
from infrastructure.repositories.template_repository import TemplateRepository


def setup_channel_with_template(channel_repo, template_repo, channel_number: int, file_path: str):
    template = template_repo.create(name="Test Template", file_path=file_path)
    channel_repo.create(
        channel_number=channel_number,
        description="Test Channel",
        template_id=template.id,
        document_source="INTERNAL"
    )


def test_create_print_job_success(client):
    template_repo = TemplateRepository(engine)
    channel_repo = ChannelRepository(engine)
    setup_channel_with_template(channel_repo, template_repo, channel_number=1, file_path="labels/test.zpl")

    payload = {
        "channel": 1,
        "client_code": "CL001",
        "client_name": "Cliente de Prueba E2E",
        "payload": {
            "to": "John Doe",
            "address": "Main St 123",
            "city": "Springfield",
            "packages": "1",
            "transport": "OCA"
        }
    }
    
    response = client.post("/print-jobs", json=payload)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["client_code"] == "CL001"
    assert data["status"] == "pending"
    assert data["channel"] == 1
    assert "id" in data
    assert "date_created" in data

    with Session(engine) as session:
        job = session.get(PrintJob, data["id"])
        assert job is not None
        assert job.client_name == "Cliente de Prueba E2E"
        assert job.status == "pending"


def test_create_print_job_validation_error(client):
    template_repo = TemplateRepository(engine)
    channel_repo = ChannelRepository(engine)
    setup_channel_with_template(channel_repo, template_repo, channel_number=1, file_path="labels/test.zpl")

    payload = {
        "channel": 1,
        "client_name": "Incompleto"
    }
    
    response = client.post("/print-jobs", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_job_copies_zero(client):
    template_repo = TemplateRepository(engine)
    channel_repo = ChannelRepository(engine)
    setup_channel_with_template(channel_repo, template_repo, channel_number=1, file_path="labels/test.zpl")

    payload = {
        "channel": 1,
        "client_code": "CL001",
        "client_name": "Cliente Test",
        "payload": {"to": "Test", "address": "Test", "city": "Test", "packages": "1", "transport": "OCA"},
        "number_of_copies": 0
    }
    
    response = client.post("/print-jobs", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_job_copies_negative(client):
    template_repo = TemplateRepository(engine)
    channel_repo = ChannelRepository(engine)
    setup_channel_with_template(channel_repo, template_repo, channel_number=1, file_path="labels/test.zpl")

    payload = {
        "channel": 1,
        "client_code": "CL001",
        "client_name": "Cliente Test",
        "payload": {"to": "Test", "address": "Test", "city": "Test", "packages": "1", "transport": "OCA"},
        "number_of_copies": -5
    }
    
    response = client.post("/print-jobs", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_job_copies_over_100(client):
    template_repo = TemplateRepository(engine)
    channel_repo = ChannelRepository(engine)
    setup_channel_with_template(channel_repo, template_repo, channel_number=1, file_path="labels/test.zpl")

    payload = {
        "channel": 1,
        "client_code": "CL001",
        "client_name": "Cliente Test",
        "payload": {"to": "Test", "address": "Test", "city": "Test", "packages": "1", "transport": "OCA"},
        "number_of_copies": 101
    }
    
    response = client.post("/print-jobs", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_job_copies_string(client):
    template_repo = TemplateRepository(engine)
    channel_repo = ChannelRepository(engine)
    setup_channel_with_template(channel_repo, template_repo, channel_number=1, file_path="labels/test.zpl")

    payload = {
        "channel": 1,
        "client_code": "CL001",
        "client_name": "Cliente Test",
        "payload": {"to": "Test", "address": "Test", "city": "Test", "packages": "1", "transport": "OCA"},
        "number_of_copies": "abc"
    }
    
    response = client.post("/print-jobs", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_job_copies_valid(client):
    template_repo = TemplateRepository(engine)
    channel_repo = ChannelRepository(engine)
    setup_channel_with_template(channel_repo, template_repo, channel_number=1, file_path="labels/test.zpl")

    payload = {
        "channel": 1,
        "client_code": "CL001",
        "client_name": "Cliente Test",
        "payload": {"to": "Test", "address": "Test", "city": "Test", "packages": "1", "transport": "OCA"},
        "number_of_copies": 50
    }
    
    response = client.post("/print-jobs", json=payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["number_of_copies"] == 50


def test_create_job_default_copies(client):
    template_repo = TemplateRepository(engine)
    channel_repo = ChannelRepository(engine)
    setup_channel_with_template(channel_repo, template_repo, channel_number=1, file_path="labels/test.zpl")

    payload = {
        "channel": 1,
        "client_code": "CL001",
        "client_name": "Cliente Test",
        "payload": {"to": "Test", "address": "Test", "city": "Test", "packages": "1", "transport": "OCA"}
    }
    
    response = client.post("/print-jobs", json=payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["number_of_copies"] == 1
