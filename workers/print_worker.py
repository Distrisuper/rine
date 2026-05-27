import logging
import time
from datetime import datetime, timedelta
from typing import Any

from sqlmodel import Session, select

from domain.entities.print_job import PrintJob
from domain.repositories.printer_repository_interface import PrinterRepositoryInterface
from domain.services.printer_discovery_interface import PrinterDiscovery
from infrastructure.repositories.printer_repository import PrinterRepository
from infrastructure.services.printer_discovery_service import CupsPrinterDiscoveryService
from application.use_cases.print_jobs.print.print_job_use_case import PrintJobUseCase
from infrastructure.api.container import container  # Asegura inyección de builders

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PrintWorker:
    POLL_INTERVAL = 5
    MAX_RETRIES = 3
    LOCK_TIMEOUT = 60

    def __init__(self, engine, printer_discovery: PrinterDiscovery | None = None):
        self.engine = engine
        self.printer_repo: PrinterRepositoryInterface = PrinterRepository(engine)
        self.printer_discovery = printer_discovery or CupsPrinterDiscoveryService()
        self.print_use_case = PrintJobUseCase()

    def run_forever(self):
        logger.info("Worker iniciado, esperando jobs...")
        while True:
            try:
                self._process_one_job()
            except Exception as e:
                logger.error(f"Error en ciclo de worker: {e}")
            time.sleep(self.POLL_INTERVAL)

    def _process_one_job(self):
        with Session(self.engine) as session:
            job = self._get_next_pending_job(session)
            if not job:
                return

            logger.info(f"Procesando job {job.id} - channel={job.channel}")

            try:
                printer = self.printer_repo.get_printer_for_channel(job.channel)

                if not printer:
                    raise Exception(f"No hay impresora configurada para channel {job.channel}")

                if not printer.is_active:
                    raise Exception(f"Impresora {printer.name} está inactiva")

                self._ensure_printer_is_ready(printer.name)

                # Renderizado unificado
                result = job.render(session)

                # Envío directo usando la info del paquete RenderedDocument
                job_id = self._send_to_printer(
                    printer_name=printer.name,
                    content=result.content,
                    content_type=result.content_type,
                    job_title=result.title,
                    number_of_copies=job.number_of_copies
                )

                job.cups_job_id = job_id
                job.status = "sent"
                job.attempt_count += 1
                job.printer_name = printer.name
                job.processing_since = None

                logger.info(f"Job {job.id} ({result.title}) enviado a {printer.name} (CUPS id={job_id})")

            except Exception as e:
                logger.error(f"Job {job.id} falló: {e}")
                self._handle_failure(job, str(e))

            session.commit()

    def _get_next_pending_job(self, session: Session) -> PrintJob | None:
        timeout = datetime.utcnow() - timedelta(seconds=self.LOCK_TIMEOUT)

        statement = (
            select(PrintJob)
            .where(PrintJob.status == "pending")
            .where(
                (PrintJob.processing_since == None) |
                (PrintJob.processing_since < timeout)
            )
            .order_by(PrintJob.date_created)
            .limit(1)
            .with_for_update(skip_locked=True)
        )

        job = session.exec(statement).first()

        if job:
            job.processing_since = datetime.utcnow()

        return job

    def _send_to_printer(self, printer_name: str, content: bytes, content_type: str, job_title: str, number_of_copies: int = 1) -> int:
        logger.info(f"Enviando a {printer_name} (type={content_type})")
        job_id = self.print_use_case(printer_name, content, content_type, job_title, number_of_copies)
        logger.info(f"Trabajo enviado a CUPS: job_id={job_id}")
        return job_id

    def _ensure_printer_is_ready(self, printer_name: str) -> None:
        printer_status = self.printer_discovery.get_printer_status(printer_name)
        if printer_status is None:
            raise Exception(f"No se pudo obtener estado de CUPS para printer_name={printer_name}")

        if printer_status.get("ready") is True:
            return

        raise Exception(self._build_printer_status_error_message(printer_name, printer_status))

    def _build_printer_status_error_message(
        self, printer_name: str, printer_status: dict[str, Any]
    ) -> str:
        details = printer_status.get("detalles")
        if isinstance(details, list):
            normalized_details = [
                str(detail).strip() for detail in details if str(detail).strip()
            ]
            if normalized_details:
                return ", ".join(normalized_details)

        return f"No se pudo obtener estado de CUPS para printer_name={printer_name}"

    def _handle_failure(self, job: PrintJob, error: str):
        job.attempt_count += 1
        job.error_message = error

        if job.attempt_count >= self.MAX_RETRIES:
            job.status = "failed"
            logger.error(f"Job {job.id} falló definitivamente")
        else:
            job.status = "pending"
            logger.warning(f"Job {job.id} reintentará ({job.attempt_count}/{self.MAX_RETRIES})")

        job.processing_since = None


if __name__ == "__main__":
    from infrastructure.db.database import engine
    worker = PrintWorker(engine)
    worker.run_forever()
