import pytest
from unittest.mock import patch
from sqlmodel import Session
from domain.entities.print_job import PrintJob
# Forzamos la importación absoluta desde la raíz
from workers.status_worker import StatusWorker
from infrastructure.db.database import engine

def test_status_worker_updates_to_printed(test_engine):
    # Setup: Create a job in 'sent' status
    with Session(test_engine) as session:
        job = PrintJob(
            client_code="S1",
            client_name="Status Test",
            channel=1,
            status="sent",
            cups_job_id=888,
            printer_name="Test Printer",
            payload='{}'
        )
        session.add(job)
        session.commit()
        job_id = job.id

    worker = StatusWorker(test_engine)
    
    # Mock CUPS response for completed job (state 9)
    mock_cups_job = {"job-state": 9}
    
    with patch.object(worker, "_get_cups_job", return_value=mock_cups_job):
        worker._check_sent_jobs()

    # Verify results in DB
    with Session(test_engine) as session:
        updated_job = session.get(PrintJob, job_id)
        assert updated_job.status == "printed"
        assert updated_job.date_processed is not None
