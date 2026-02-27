import logging
import time
from datetime import datetime
from sqlmodel import Session, select

from domain.entities.print_job import PrintJob

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

try:
    import cups
    CUPS_AVAILABLE = True
except ImportError:
    CUPS_AVAILABLE = False
    cups = None

CUPS_JOB_STATES = {
    3: "pending",
    4: "held",
    5: "processing",
    6: "stopped",
    7: "canceled",
    8: "aborted",
    9: "completed",
}


class StatusWorker:
    POLL_INTERVAL = 10
    MAX_WAIT_SECONDS = 60
    MAX_RETRIES = 3

    def __init__(self, engine):
        self.engine = engine

    def run_forever(self):
        logger.info("StatusWorker iniciado, monitoreando jobs en CUPS...")
        while True:
            try:
                self._check_sent_jobs()
            except Exception as e:
                logger.error(f"Error en StatusWorker: {e}")
            time.sleep(self.POLL_INTERVAL)

    def _check_sent_jobs(self):
        with Session(self.engine) as session:
            statement = (
                select(PrintJob)
                .where(PrintJob.status == "sent")
            )
            jobs = session.exec(statement).all()

            if not jobs:
                return

            logger.info(f"Verificando {len(jobs)} job(s) en CUPS")

            for job in jobs:
                self._check_job_status(job, session)

            session.commit()

    def _check_job_status(self, job: PrintJob, session: Session):
        if not job.cups_job_id or not job.printer_name:
            logger.warning(f"Job {job.id} sin cups_job_id o printer_name, marcando como failed")
            job.status = "failed"
            job.error_message = "Sin cups_job_id o printer_name"
            return

        try:
            cups_job = self._get_cups_job(job.printer_name, job.cups_job_id)
            
            if cups_job is None:
                self._handle_job_not_found(job, session)
                return

            state = cups_job.get("job-state", 0)
            state_name = CUPS_JOB_STATES.get(state, "unknown")

            logger.debug(f"Job {job.id}: CUPS state={state} ({state_name})")

            if state in (7, 8):
                job.status = "failed"
                job.error_message = f"CUPS job state: {state_name}"
                logger.warning(f"Job {job.id} falló en CUPS: {state_name}")

            elif state == 9:
                job.status = "printed"
                job.date_processed = datetime.utcnow()
                logger.info(f"Job {job.id} completado exitosamente en CUPS")

            elif state == 3:
                wait_time = (datetime.utcnow() - job.date_created).total_seconds()
                if wait_time > self.MAX_WAIT_SECONDS:
                    job.status = "failed"
                    job.error_message = f"Timeout esperando en CUPS ({wait_time}s)"
                    logger.error(f"Job {job.id} timeout en CUPS")

        except Exception as e:
            logger.error(f"Error verificando job {job.id}: {e}")
            self._handle_check_error(job, session, str(e))

    def _get_cups_job(self, printer_name: str, cups_job_id: int) -> dict | None:
        if not CUPS_AVAILABLE or cups is None:
            logger.error("CUPS no disponible (pycups no instalado)")
            return None

        try:
            conn = cups.Connection()
            jobs = conn.getJobs(which_jobs="not-completed", my_jobs=False)
            
            if cups_job_id in jobs:
                job_info = jobs[cups_job_id]
                return {"job-state": job_info.get("job-state", 0)}
            
            jobs_completed = conn.getJobs(which_jobs="completed", my_jobs=False)
            if cups_job_id in jobs_completed:
                job_info = jobs_completed[cups_job_id]
                return {"job-state": job_info.get("job-state", 9)}

            return None
        except Exception as e:
            logger.error(f"Error consultando CUPS para job {cups_job_id}: {e}")
            return None

    def _handle_job_not_found(self, job: PrintJob, session: Session):
        if job.print_count >= self.MAX_RETRIES:
            job.status = "failed"
            job.error_message = f"Job {job.cups_job_id} no encontrado en CUPS después de {job.print_count} intentos"
            logger.error(f"Job {job.id} falló: no encontrado en CUPS")
        else:
            job.print_count += 1
            logger.warning(f"Job {job.id} no encontrado en CUPS, incrementando retry ({job.print_count})")

    def _handle_check_error(self, job: PrintJob, session: Session, error: str):
        job.print_count += 1
        job.error_message = f"Error verificando: {error}"

        if job.print_count >= self.MAX_RETRIES:
            job.status = "failed"
            logger.error(f"Job {job.id} falló definitivamente tras {job.print_count} errores")


if __name__ == "__main__":
    from infrastructure.db.database import engine
    worker = StatusWorker(engine)
    worker.run_forever()
