import logging
import time
from datetime import datetime, timedelta

from sqlmodel import Session, select

from domain.entities.print_job import PrintJob
from domain.repositories.printer_repository import PrinterRepository
from application.use_cases.print_jobs.print.print_job_use_case import PrintJobUseCase

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PrintWorker:
    POLL_INTERVAL = 5
    MAX_RETRIES = 3
    LOCK_TIMEOUT = 60

    def __init__(self, engine):
        self.engine = engine
        self.printer_repo = PrinterRepository(engine)
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

                content = job.render()

                template = job.get_template()
                content_type = "pdf"
                job_title = "PrintJob"
                if template and template.file_path.lower().endswith(".zpl"):
                    content_type = "zpl"
                    job_title = "Etiqueta"

                job_id = self._send_to_printer(printer.name, content, content_type, job_title)

                job.cups_job_id = job_id
                job.status = "sent"
                job.print_count += 1
                job.printer_name = printer.name
                job.processing_since = None

                logger.info(f"Job {job.id} enviado a {printer.name} (CUPS job_id={job_id})")

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
        )

        job = session.exec(statement).first()

        if job:
            job.processing_since = datetime.utcnow()
            session.commit()

        return job

    def _send_to_printer(self, printer_name: str, content: bytes, content_type: str, job_title: str) -> int:
        logger.info(f"Enviando a {printer_name} (type={content_type})")
        job_id = self.print_use_case(printer_name, content, content_type, job_title)
        logger.info(f"Trabajo enviado a CUPS: job_id={job_id}")
        return job_id

    def _handle_failure(self, job: PrintJob, error: str):
        job.print_count += 1
        job.error_message = error

        if job.print_count >= self.MAX_RETRIES:
            job.status = "failed"
            logger.error(f"Job {job.id} falló definitivamente")
        else:
            job.status = "pending"
            logger.warning(f"Job {job.id} reintentará ({job.print_count}/{self.MAX_RETRIES})")

        job.processing_since = None


if __name__ == "__main__":
    from infrastructure.db.database import engine
    worker = PrintWorker(engine)
    worker.run_forever()
