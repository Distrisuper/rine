import pytest
from unittest.mock import MagicMock, patch
from sqlmodel import Session, select
from datetime import datetime

from domain.entities.print_job import PrintJob
from domain.entities.printer import Printer
from domain.entities.channel import Channel
from domain.entities.template import Template
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
        mock.return_value = b"Fake PDF Content"
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
    channel = channel_repo.create(channel_number=10, description="Test Channel", template_id=template.id)
    
    # Link Printer to Channel via repository (create_printer also links channels)
    printer_repo.create_printer(name="TestPrinter", channel_ids=[channel.id])

    # Create Pending Print Job
    job = PrintJob(
        client_code="C001",
        client_name="Test Client",
        channel=10,
        payload='{"to": "John Doe", "address": "Street 123", "city": "City", "packages": "1/1"}',
        status="pending",
        number_of_copies=2,
        attempt_count=0
    )
    print_job_repo.create(job)
    job_id = job.id

    # 2. Run Worker (single pass)
    worker = PrintWorker(test_engine)
    worker._process_one_job()

    # 3. Verify Results
    updated_job = print_job_repo.get_by_id(job_id)
    assert updated_job.status == "sent"
    assert updated_job.cups_job_id == 12345
    assert updated_job.printer_name == "TestPrinter"
    assert updated_job.attempt_count == 1
    assert updated_job.processing_since is None

def test_print_worker_handles_missing_printer(test_engine, mock_render):
    # Setup job for a channel that has no printer
    print_job_repo = PrintJobRepository(test_engine)
    
    job = PrintJob(
        client_code="C002",
        client_name="No Printer Client",
        channel=99, # Non-existent channel/printer
        payload='{}',
        status="pending",
        number_of_copies=1,
        attempt_count=0
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

def test_print_worker_passes_number_of_copies_to_cups(test_engine, mock_cups, mock_render):
    # Setup Data
    template_repo = TemplateRepository(test_engine)
    channel_repo = ChannelRepository(test_engine)
    printer_repo = PrinterRepository(test_engine)
    print_job_repo = PrintJobRepository(test_engine)

    # Create Template, Channel, Printer
    template = template_repo.create(name="Test Template", file_path="test.html")
    channel = channel_repo.create(channel_number=10, description="Test Channel", template_id=template.id)
    printer_repo.create_printer(name="TestPrinter", channel_ids=[channel.id])

    # Create Print Job with 3 copies
    job = PrintJob(
        client_code="C001",
        client_name="Test Client",
        channel=10,
        payload='{"to": "John Doe", "address": "Street 123", "city": "City", "packages": "1/1"}',
        status="pending",
        number_of_copies=3,
        attempt_count=0
    )
    print_job_repo.create(job)
    job_id = job.id

    # Run Worker
    worker = PrintWorker(test_engine)
    worker._process_one_job()

    # Verify: CUPS printFile was called with copies option
    assert mock_cups.Connection.return_value.printFile.called
    
    # Get the call arguments
    call_args = mock_cups.Connection.return_value.printFile.call_args
    # call_args[1] contains keyword arguments
    options = call_args[1] if call_args[1] else {}
    
    # Verify that 'copies' was passed in options
    assert "copies" in options or (call_args[0][-1] and "copies" in call_args[0][-1])
    
    # Verify job status is updated
    updated_job = print_job_repo.get_by_id(job_id)
    assert updated_job.status == "sent"
    assert updated_job.attempt_count == 1
    assert updated_job.number_of_copies == 3  # Never changes, it's the desired quantity
