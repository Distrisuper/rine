"""
Envío de trabajos de impresión a CUPS.
Solo funciona en Linux con CUPS y pycups; en Windows no hay envío real.
"""
import os
import logging
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    import cups
    CUPS_AVAILABLE = True
    # Configurar servidor remoto si existe la variable
    cups_server = os.getenv("CUPS_SERVER")
    if cups_server:
        cups.setServer(cups_server)
        # Forzar encriptación desactivada para evitar Bad Request (1024)
        cups.setEncryption(cups.HTTP_ENCRYPT_NEVER)
        logger.info(f"Servidor CUPS configurado: {cups_server} (Encriptación: Never)")
except ImportError:
    CUPS_AVAILABLE = False
    cups = None


def print_pdf_to_printer(printer_name: str, pdf_bytes: bytes, job_title: str = "Remito", number_of_copies: int = 1) -> int:
    """
    Envía un PDF a una cola CUPS por nombre.
    """
    if not CUPS_AVAILABLE or cups is None:
        raise RuntimeError("CUPS no disponible (solo Linux con pycups)")

    # Usamos mkstemp para asegurar que el archivo se cierre antes de que CUPS lo lea
    fd, path_str = tempfile.mkstemp(suffix=".pdf")
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(pdf_bytes)
            f.flush()
            os.fsync(f.fileno())
        
        conn = cups.Connection()
        options = {"copies": str(number_of_copies)}
        job_id = conn.printFile(printer_name, path_str, job_title, options)
        logger.info("Trabajo PDF enviado a %s: job_id=%s, size=%s bytes", printer_name, job_id, len(pdf_bytes))
        return job_id
    finally:
        if os.path.exists(path_str):
            os.unlink(path_str)


def print_raw_to_printer(
    printer_name: str,
    raw_bytes: bytes,
    job_title: str = "Etiqueta",
    number_of_copies: int = 1,
    suffix: str = ".zpl",
) -> int:
    """
    Envía datos en bruto (ZPL) a una cola CUPS.
    """
    if not CUPS_AVAILABLE or cups is None:
        raise RuntimeError("CUPS no disponible (solo Linux con pycups)")

    fd, path_str = tempfile.mkstemp(suffix=suffix)
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(raw_bytes)
            f.flush()
            os.fsync(f.fileno())

        conn = cups.Connection()
        options = {"copies": str(number_of_copies)}
        job_id = conn.printFile(printer_name, path_str, job_title, options)
        logger.info("Trabajo RAW enviado a %s: job_id=%s, size=%s bytes", printer_name, job_id, len(raw_bytes))
        return job_id
    finally:
        if os.path.exists(path_str):
            os.unlink(path_str)
