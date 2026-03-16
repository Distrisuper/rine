import logging
import time
from datetime import datetime
from typing import Any
from sqlmodel import Session

from domain.entities.print_job import PrintJob
from domain.repositories.print_job_repository_interface import PrintJobRepositoryInterface
from infrastructure.repositories.print_job_repository import PrintJobRepository

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

PRINTER_UNAVAILABLE_REASONS = frozenset({
    "offline",
    "stopped",
    "paused",
    "printer-error",
    "media-empty",
    "media-needed",
    "paper-empty",
    "paper-needed",
    "marker-supply-empty",
    "marker-supply-low",
    "ribbon-empty",
    "ribbon-low",
    "label-empty",
    "labels-needed",
    "toner-empty",
    "toner-low",
    "door-open",
    "cover-open",
})

PRINTER_UNAVAILABLE_REASON_MESSAGES = {
    "offline": "Impresora desconectada",
    "stopped": "Impresora detenida",
    "paused": "Impresora en pausa",
    "printer-error": "Error de impresora",
    "media-empty": "Sin papel/medio",
    "media-needed": "Medio requerido",
    "paper-empty": "Sin papel",
    "paper-needed": "Papel requerido",
    "marker-supply-empty": "Sin insumo",
    "marker-supply-low": "Insumo bajo",
    "ribbon-empty": "Sin ribbon",
    "ribbon-low": "Ribbon bajo",
    "label-empty": "Sin etiquetas",
    "labels-needed": "Etiquetas requeridas",
    "toner-empty": "Sin tóner",
    "toner-low": "Tóner bajo",
    "door-open": "Puerta abierta",
    "cover-open": "Tapa abierta",
}

PRINTER_UNAVAILABLE_MESSAGE_KEYWORDS = (
    "offline",
    "unavailable",
    "not available",
    "cannot connect",
    "connection refused",
    "timed out",
    "apagada",
    "desconectada",
)


class StatusWorker:
    POLL_INTERVAL = 10
    MAX_WAIT_SECONDS = 60
    MAX_RETRIES = 3

    def __init__(self, engine):
        self.engine = engine
        self.print_job_repo: PrintJobRepositoryInterface = PrintJobRepository(engine)

    def run_forever(self):
        logger.info("StatusWorker iniciado, monitoreando jobs en CUPS...")
        while True:
            try:
                self._check_sent_jobs()
            except Exception as e:
                logger.error(f"Error en StatusWorker: {e}")
            time.sleep(self.POLL_INTERVAL)

    def _check_sent_jobs(self):
        jobs, _ = self.print_job_repo.get_all(status="sent", limit=500)

        if not jobs:
            return

        logger.info(f"Verificando {len(jobs)} job(s) en CUPS")

        for job in jobs:
            self._check_job_status(job)

    def _check_job_status(self, job: PrintJob):
        if not job.cups_job_id or not job.printer_name:
            logger.warning(f"Job {job.id} sin cups_job_id o printer_name, marcando como failed")
            job.status = "failed"
            job.error_message = "Sin cups_job_id o printer_name"
            self.print_job_repo.update(job)
            return

        try:
            cups_job = self._get_cups_job(job.printer_name, job.cups_job_id)
            
            if cups_job is None:
                self._handle_job_not_found(job)
                return

            state = cups_job.get("job-state", 0)
            state_name = CUPS_JOB_STATES.get(state, "unknown")

            logger.debug(f"Job {job.id}: CUPS state={state} ({state_name})")

            if state in (7, 8):
                job.status = "failed"
                job.error_message = f"CUPS job state: {state_name}"
                logger.warning(f"Job {job.id} falló en CUPS: {state_name}")
                self.print_job_repo.update(job)
            elif state == 4:
                if self._has_printer_unavailable_evidence(cups_job):
                    job.status = "failed"
                    job.error_message = self._build_printer_unavailable_error(cups_job)
                    logger.warning(f"Job {job.id} falló por impresora no disponible: {job.error_message}")
                    self.print_job_repo.update(job)

            elif state == 9:
                job.status = "printed"
                job.date_processed = datetime.utcnow()
                logger.info(f"Job {job.id} completado exitosamente en CUPS")
                self.print_job_repo.update(job)

            elif state == 3:
                wait_time = (datetime.utcnow() - job.date_created).total_seconds()
                if wait_time > self.MAX_WAIT_SECONDS:
                    job.status = "failed"
                    job.error_message = f"Timeout esperando en CUPS ({wait_time}s)"
                    logger.error(f"Job {job.id} timeout en CUPS")
                    self.print_job_repo.update(job)

        except Exception as e:
            logger.error(f"Error verificando job {job.id}: {e}")
            self._handle_check_error(job, str(e))

    def _get_cups_job(self, printer_name: str, cups_job_id: int) -> dict[str, Any] | None:
        if not CUPS_AVAILABLE or cups is None:
            logger.error("CUPS no disponible (pycups no instalado)")
            return None

        try:
            conn = cups.Connection()
            jobs = conn.getJobs(which_jobs="not-completed", my_jobs=False)
            
            if cups_job_id in jobs:
                job_info = jobs[cups_job_id]
                return {
                    "job-state": job_info.get("job-state", 0),
                    "job-state-reasons": job_info.get("job-state-reasons"),
                    "job-printer-state-reasons": job_info.get("job-printer-state-reasons"),
                    "job-state-message": job_info.get("job-state-message"),
                    "job-printer-state-message": job_info.get("job-printer-state-message"),
                }
            
            jobs_completed = conn.getJobs(which_jobs="completed", my_jobs=False)
            if cups_job_id in jobs_completed:
                job_info = jobs_completed[cups_job_id]
                return {
                    "job-state": job_info.get("job-state", 9),
                    "job-state-reasons": job_info.get("job-state-reasons"),
                    "job-printer-state-reasons": job_info.get("job-printer-state-reasons"),
                    "job-state-message": job_info.get("job-state-message"),
                    "job-printer-state-message": job_info.get("job-printer-state-message"),
                }

            return None
        except Exception as e:
            logger.error(f"Error consultando CUPS para job {cups_job_id}: {e}")
            return None

    def _normalize_cups_reasons(self, cups_job: dict[str, Any]) -> list[str]:
        reasons_raw = (
            cups_job.get("job-state-reasons")
            or cups_job.get("job-printer-state-reasons")
            or []
        )

        if isinstance(reasons_raw, (str, bytes)):
            reasons_iterable = [reasons_raw]
        elif isinstance(reasons_raw, (list, tuple, set)):
            reasons_iterable = list(reasons_raw)
        else:
            reasons_iterable = [reasons_raw]

        normalized: list[str] = []
        for reason in reasons_iterable:
            if isinstance(reason, bytes):
                normalized.append(reason.decode("utf-8", errors="replace").strip().lower())
            else:
                normalized.append(str(reason).strip().lower())

        return [reason for reason in normalized if reason and reason != "none"]

    def _extract_cups_message(self, cups_job: dict[str, Any]) -> str:
        message = cups_job.get("job-state-message") or cups_job.get("job-printer-state-message") or ""
        if isinstance(message, bytes):
            return message.decode("utf-8", errors="replace").strip().lower()
        return str(message).strip().lower()

    def _has_printer_unavailable_evidence(self, cups_job: dict[str, Any]) -> bool:
        reasons = self._normalize_cups_reasons(cups_job)
        if any(reason in PRINTER_UNAVAILABLE_REASONS for reason in reasons):
            return True

        message = self._extract_cups_message(cups_job)
        return any(keyword in message for keyword in PRINTER_UNAVAILABLE_MESSAGE_KEYWORDS)

    def _build_printer_unavailable_error(self, cups_job: dict[str, Any]) -> str:
        reasons = self._normalize_cups_reasons(cups_job)
        for reason in reasons:
            if reason in PRINTER_UNAVAILABLE_REASON_MESSAGES:
                return f"Impresora no disponible/apagada: {PRINTER_UNAVAILABLE_REASON_MESSAGES[reason]}"
        if reasons:
            return f"Impresora no disponible/apagada: {reasons[0]}"

        message = self._extract_cups_message(cups_job)
        if message:
            return f"Impresora no disponible/apagada: {message}"

        return "Impresora no disponible/apagada"

    def _handle_job_not_found(self, job: PrintJob):
        if job.attempt_count >= self.MAX_RETRIES:
            job.status = "failed"
            job.error_message = f"Job {job.cups_job_id} no encontrado en CUPS después de {job.attempt_count} intentos"
            logger.error(f"Job {job.id} falló: no encontrado en CUPS")
        else:
            job.attempt_count += 1
            logger.warning(f"Job {job.id} no encontrado en CUPS, incrementando retry ({job.attempt_count})")
        
        self.print_job_repo.update(job)

    def _handle_check_error(self, job: PrintJob, error: str):
        job.attempt_count += 1
        job.error_message = f"Error verificando: {error}"

        if job.attempt_count >= self.MAX_RETRIES:
            job.status = "failed"
            logger.error(f"Job {job.id} falló definitivamente tras {job.attempt_count} errores")
        
        self.print_job_repo.update(job)


if __name__ == "__main__":
    from infrastructure.db.database import engine
    worker = StatusWorker(engine)
    worker.run_forever()
