import pytest
from unittest.mock import MagicMock, patch
from sqlmodel import Session
from datetime import datetime
from datetime import timedelta

from domain.entities.print_job import PrintJob
from infrastructure.repositories.print_job_repository import PrintJobRepository
from workers.status_worker import StatusWorker

@pytest.fixture
def mock_cups_status():
    with patch("workers.status_worker.cups") as mock:
        # Por defecto simulamos que el job está completado (state 9)
        mock.Connection.return_value.getJobs.return_value = {
            12345: {"job-state": 9}
        }
        yield mock

def test_status_worker_marks_job_as_printed(test_engine, mock_cups_status):
    # 1. Setup: Job enviado (sent) con cups_job_id
    print_job_repo = PrintJobRepository(test_engine)
    
    job = PrintJob(
        client_code="C001",
        client_name="Test Client",
        channel=10,
        payload='{}',
        status="sent",
        cups_job_id=12345,
        printer_name="TestPrinter"
    )
    print_job_repo.create(job)
    job_id = job.id

    # 2. Run Status Worker (single pass)
    worker = StatusWorker(test_engine)
    worker._check_sent_jobs()

    # 3. Verify: El status debe ser "printed"
    updated_job = print_job_repo.get_by_id(job_id)
    assert updated_job.status == "printed"
    assert updated_job.date_processed is not None

def test_status_worker_handles_failed_job_in_cups(test_engine, mock_cups_status):
    # Setup: Simular estado de error en CUPS (ej. state 7 = canceled o 8 = aborted)
    mock_cups_status.Connection.return_value.getJobs.return_value = {
        67890: {"job-state": 7}
    }
    
    print_job_repo = PrintJobRepository(test_engine)

    job = PrintJob(
        client_code="C002",
        client_name="Failed Client",
        channel=10,
        payload='{}',
        status="sent",
        cups_job_id=67890,
        printer_name="TestPrinter"
    )
    print_job_repo.create(job)
    job_id = job.id

    worker = StatusWorker(test_engine)
    worker._check_sent_jobs()

    updated_job = print_job_repo.get_by_id(job_id)
    assert updated_job.status == "failed"
    assert "CUPS job state: canceled" in updated_job.error_message

def test_status_worker_stays_sent_if_still_processing(test_engine, mock_cups_status):
    # Setup: Simular estado "processing" (state 5)
    mock_cups_status.Connection.return_value.getJobs.return_value = {
        55555: {"job-state": 5}
    }
    
    print_job_repo = PrintJobRepository(test_engine)

    job = PrintJob(
        client_code="C003",
        client_name="Busy Client",
        channel=10,
        payload='{}',
        status="sent",
        cups_job_id=55555,
        printer_name="TestPrinter"
    )
    print_job_repo.create(job)
    job_id = job.id

    worker = StatusWorker(test_engine)
    worker._check_sent_jobs()

    updated_job = print_job_repo.get_by_id(job_id)
    # Sigue en "sent" porque aún no termina
    assert updated_job.status == "sent"


def test_status_worker_keeps_held_job_as_sent_and_saves_description(test_engine, mock_cups_status):
    mock_cups_status.Connection.return_value.getJobs.return_value = {
        44444: {
            "job-state": 4,
            "job-state-reasons": ["offline"],
            "job-state-message": "The printer may not exist or is unavailable at this time.",
        }
    }

    print_job_repo = PrintJobRepository(test_engine)
    job = PrintJob(
        client_code="C004",
        client_name="Held Offline Client",
        channel=10,
        payload='{}',
        status="sent",
        cups_job_id=44444,
        printer_name="TestPrinter",
    )
    print_job_repo.create(job)
    job_id = job.id

    worker = StatusWorker(test_engine)
    worker._check_sent_jobs()

    updated_job = print_job_repo.get_by_id(job_id)
    assert updated_job.status == "sent"
    assert "CUPS held:" in (updated_job.error_message or "")
    assert "offline" in (updated_job.error_message or "")


def test_status_worker_keeps_held_job_as_sent_with_non_critical_reason(test_engine, mock_cups_status):
    mock_cups_status.Connection.return_value.getJobs.return_value = {
        55556: {
            "job-state": 4,
            "job-state-reasons": ["job-data-insufficient"],
            "job-state-message": "Job is held for policy check",
        }
    }

    print_job_repo = PrintJobRepository(test_engine)
    job = PrintJob(
        client_code="C005",
        client_name="Held Policy Client",
        channel=10,
        payload='{}',
        status="sent",
        cups_job_id=55556,
        printer_name="TestPrinter",
    )
    print_job_repo.create(job)
    job_id = job.id

    worker = StatusWorker(test_engine)
    worker._check_sent_jobs()

    updated_job = print_job_repo.get_by_id(job_id)
    assert updated_job.status == "sent"
    assert "CUPS held:" in (updated_job.error_message or "")
    assert "policy check" in (updated_job.error_message or "").lower()


def test_status_worker_does_not_timeout_based_on_date_created_if_date_sent_is_recent(
    test_engine, mock_cups_status
):
    mock_cups_status.Connection.return_value.getJobs.return_value = {
        99999: {"job-state": 3}
    }

    print_job_repo = PrintJobRepository(test_engine)
    job = PrintJob(
        client_code="C006",
        client_name="Recent Sent Client",
        channel=10,
        payload="{}",
        status="sent",
        cups_job_id=99999,
        printer_name="TestPrinter",
        date_created=datetime.utcnow() - timedelta(hours=2),
        date_sent=datetime.utcnow(),
    )
    print_job_repo.create(job)
    job_id = job.id

    worker = StatusWorker(test_engine)
    worker._check_sent_jobs()

    updated_job = print_job_repo.get_by_id(job_id)
    assert updated_job.status == "sent"


def test_status_worker_checks_more_than_500_sent_jobs(test_engine):
    print_job_repo = PrintJobRepository(test_engine)
    for i in range(600):
        job = PrintJob(
            client_code=f"C{i:04d}",
            client_name="Bulk Client",
            channel=10,
            payload="{}",
            status="sent",
            cups_job_id=100000 + i,
            printer_name="TestPrinter",
        )
        print_job_repo.create(job)

    worker = StatusWorker(test_engine)
    checked_ids: list[int] = []

    def record(job: PrintJob) -> None:
        checked_ids.append(job.id or 0)

    worker._check_job_status = record  # type: ignore[method-assign]
    worker._check_sent_jobs()

    assert len(checked_ids) == 600
