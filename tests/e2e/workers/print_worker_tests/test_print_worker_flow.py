import pytest
from unittest.mock import MagicMock, patch
from sqlmodel import Session, select
from datetime import datetime

from domain.entities.print_job import PrintJob
from domain.entities.printer import Printer
from domain.entities.channel import Channel
from domain.entities.template import Template
from domain.value_objects.rendered_document import RenderedDocument
from infrastructure.repositories.printer_repository import PrinterRepository
from infrastructure.repositories.channel_repository import ChannelRepository
from infrastructure.repositories.template_repository import TemplateRepository
from infrastructure.repositories.print_job_repository import PrintJobRepository
from workers.print_worker import PrintWorker

@pytest.fixture
def mock_cups():
    with patch("infrastructure.services.print_job_service.cups") as mock:
        mock.Connection.return_value.getPrinters.return_value = {"TestPrinter": {}}
        mock.Connection.return_value.printFile.return_value = 12345
        yield mock

@pytest.fixture
def mock_render():
    with patch("domain.entities.print_job.PrintJob.render") as mock:
        mock.return_value = RenderedDocument(
            content=b"Fake PDF Content",
            content_type="pdf",
            title="Remito"
        )
        yield mock

def test_print_worker_processes_pending_job(test_engine, mock_cups, mock_render):
    # 1. Setup Data using repositories
    template_repo = TemplateRepository(test_engine)
    channel_repo = ChannelRepository(test_engine)
    printer_repo = PrinterRepository(test_engine)
    print_job_repo = PrintJobRepository(test_engine)

    # Create Template
    template = template_repo.create(name="Test Template", file_path="test.html")

    # Create Channel linked to Template
    channel = channel_repo.create(channel_number=10, description="Test Channel", template_id=template.id, document_source="INTERNAL")
    
    # Link Printer to Channel via repository (create_printer also links channels)
    printer_repo.create_printer(name="TestPrinter", channel_ids=[channel.id])

    # Create Pending Print Job
    job = PrintJob(
        client_code="C001",
        client_name="Test Client",
        channel=10,
        payload='{"to": "John Doe", "address": "Street 123", "city": "City", "packages": "1/1"}',
        status="pending"
    )
    print_job_repo.create(job)
    job_id = job.id

    # 2. Run Worker (single pass)
    printer_discovery = MagicMock()
    printer_discovery.get_printer_status.return_value = {
        "ready": True,
        "detalles": [],
    }

    worker = PrintWorker(test_engine, printer_discovery=printer_discovery)
    worker._process_one_job()

    # 3. Verify Results
    updated_job = print_job_repo.get_by_id(job_id)
    assert updated_job.status == "sent"
    assert updated_job.cups_job_id == 12345
    assert updated_job.printer_name == "TestPrinter"
    assert updated_job.attempt_count == 0
    assert updated_job.processing_since is None
    assert updated_job.date_started is not None
    assert updated_job.date_sent is not None
    printer_discovery.get_printer_status.assert_called_once_with("TestPrinter")

def test_print_worker_handles_missing_printer(test_engine, mock_render):
    # Setup job for a channel that has no printer
    print_job_repo = PrintJobRepository(test_engine)
    
    job = PrintJob(
        client_code="C002",
        client_name="No Printer Client",
        channel=99, # Non-existent channel/printer
        payload='{}',
        status="pending"
    )
    print_job_repo.create(job)
    job_id = job.id

    worker = PrintWorker(test_engine)
    worker._process_one_job()

    updated_job = print_job_repo.get_by_id(job_id)
    # Should retry or fail depending on MAX_RETRIES. Default MAX_RETRIES is 3.
    # After 1st failure, it should still be "pending" but with attempt_count=1 and error_message
    assert updated_job.status == "pending"
    assert updated_job.attempt_count == 1
    assert "No hay impresora configurada" in updated_job.error_message


def test_print_worker_retries_when_printer_is_not_ready(test_engine, mock_cups, mock_render):
    template_repo = TemplateRepository(test_engine)
    channel_repo = ChannelRepository(test_engine)
    printer_repo = PrinterRepository(test_engine)
    print_job_repo = PrintJobRepository(test_engine)

    template = template_repo.create(name="Test Template", file_path="test.html")
    channel = channel_repo.create(
        channel_number=11,
        description="Blocked Channel",
        template_id=template.id,
        document_source="INTERNAL",
    )
    printer_repo.create_printer(name="BlockedPrinter", channel_ids=[channel.id])

    job = PrintJob(
        client_code="C003",
        client_name="Blocked Client",
        channel=11,
        payload='{"to": "Jane Doe"}',
        status="pending",
    )
    print_job_repo.create(job)
    job_id = job.id

    printer_discovery = MagicMock()
    printer_discovery.get_printer_status.return_value = {
        "ready": False,
        "detalles": ["paper-empty", "paused"],
    }

    worker = PrintWorker(test_engine, printer_discovery=printer_discovery)
    worker._process_one_job()

    updated_job = print_job_repo.get_by_id(job_id)
    assert updated_job.status == "pending"
    assert updated_job.attempt_count == 1
    assert updated_job.error_message == "paper-empty, paused"
    assert updated_job.cups_job_id is None


def test_print_worker_uses_technical_fallback_when_status_is_unavailable(
    test_engine, mock_cups, mock_render
):
    template_repo = TemplateRepository(test_engine)
    channel_repo = ChannelRepository(test_engine)
    printer_repo = PrinterRepository(test_engine)
    print_job_repo = PrintJobRepository(test_engine)

    template = template_repo.create(name="Test Template", file_path="test.html")
    channel = channel_repo.create(
        channel_number=12,
        description="Unavailable Channel",
        template_id=template.id,
        document_source="INTERNAL",
    )
    printer_repo.create_printer(name="UnavailablePrinter", channel_ids=[channel.id])

    job = PrintJob(
        client_code="C004",
        client_name="Unavailable Client",
        channel=12,
        payload='{"to": "Jane Doe"}',
        status="pending",
        attempt_count=2,
    )
    print_job_repo.create(job)
    job_id = job.id

    printer_discovery = MagicMock()
    printer_discovery.get_printer_status.return_value = None

    worker = PrintWorker(test_engine, printer_discovery=printer_discovery)
    worker._process_one_job()

    updated_job = print_job_repo.get_by_id(job_id)
    assert updated_job.status == "failed"
    assert updated_job.attempt_count == 3
    assert (
        updated_job.error_message
        == "No se pudo obtener estado de CUPS para printer_name=UnavailablePrinter"
    )
    assert updated_job.cups_job_id is None
