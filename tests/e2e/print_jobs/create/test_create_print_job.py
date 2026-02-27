import json

import pytest
from sqlmodel import Session, select

from application.use_cases.print_jobs.create.create_print_job_use_case import (
    CreatePrintJobUseCase,
)
from domain.entities.print_job import PrintJob


class TestCreatePrintJobUseCase:
    @pytest.fixture
    def use_case(self):
        return CreatePrintJobUseCase()

    def test_create_print_job_success(self, use_case):
        result = use_case(
            channel=1,
            client_code="CL001",
            client_name="Test Client",
            payload={"type": "ETIQ", "package_quantity": 5},
        )

        assert result["status"] == "pending"
        assert result["document_type"] == "channel_1"
        assert "id" in result
        assert "date_created" in result

    def test_create_job_returns_correct_structure(self, use_case):
        result = use_case(
            channel=3,
            client_code="CL999",
            client_name="Cliente Prueba",
            payload={"type": "REMI"},
        )

        assert "id" in result
        assert result["status"] == "pending"
        assert result["document_type"] == "channel_3"
        assert isinstance(result["date_created"], str)

    def test_create_job_persists_to_db(self, use_case, test_engine):
        client_code = "CL persistence test"

        result = use_case(
            channel=2,
            client_code=client_code,
            client_name="Client Persisted",
            payload={"test": True},
        )

        job_id = result["id"]

        with Session(test_engine) as session:
            job = session.get(PrintJob, job_id)
            assert job is not None
            assert job.client_code == client_code
            assert job.channel == 2
            assert job.status == "pending"
            assert json.loads(job.payload) == {"test": True}

    def test_create_job_increments_print_count(self, use_case, test_engine):
        result = use_case(
            channel=1,
            client_code="CL_COUNT",
            client_name="Count Test",
            payload={},
        )

        with Session(test_engine) as session:
            job = session.get(PrintJob, result["id"])
            assert job.print_count == 0
