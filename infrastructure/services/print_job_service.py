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
    Requiere Linux con CUPS y la impresora ya configurada en CUPS.

    Args:
        printer_name: Nombre de la impresora en CUPS.
        pdf_bytes: Contenido del PDF a imprimir.
        job_title: Título del trabajo de impresión.
        number_of_copies: Número de copias a imprimir.

    Returns:
        job_id del trabajo enviado a CUPS.

    Raises:
        RuntimeError: si CUPS no está disponible (ej. Windows).
        ValueError: si la impresora no existe o falla el envío.
    """
    if not CUPS_AVAILABLE or cups is None:
        raise RuntimeError("CUPS no disponible (solo Linux con pycups)")

    conn = cups.Connection()
    printers = conn.getPrinters()
    if printer_name not in printers:
        raise ValueError(f"Impresora '{printer_name}' no existe en CUPS. Disponibles: {list(printers.keys())}")

    # CUPS requiere archivo en disco; limpiamos en finally. Si el proceso termina
    # por SIGKILL/crash antes del finally, el temp puede quedar en el FS (edge case).
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(pdf_bytes)
        path = Path(f.name)

    try:
        options = {"copies": str(number_of_copies)}
        job_id = conn.printFile(printer_name, str(path), job_title, options)
        logger.info("Trabajo enviado a %s: job_id=%s, copies=%s", printer_name, job_id, number_of_copies)
        return job_id
    finally:
        path.unlink(missing_ok=True)


def print_raw_to_printer(
    printer_name: str,
    raw_bytes: bytes,
    job_title: str = "Etiqueta",
    number_of_copies: int = 1,
    suffix: str = ".zpl",
) -> int:
    """
    Envía datos en bruto (ej. ZPL) a una cola CUPS por nombre.
    Pensado para impresoras de etiquetas (Zebra) configuradas con cola raw (-m raw).

    Args:
        printer_name: Nombre de la impresora en CUPS.
        raw_bytes: Contenido en bruto a imprimir.
        job_title: Título del trabajo de impresión.
        number_of_copies: Número de copias a imprimir.
        suffix: Extensión del archivo temporal.

    Returns:
        job_id del trabajo enviado a CUPS.

    Raises:
        RuntimeError: si CUPS no está disponible (ej. Windows).
        ValueError: si la impresora no existe o falla el envío.
    """
    if not CUPS_AVAILABLE or cups is None:
        raise RuntimeError("CUPS no disponible (solo Linux con pycups)")

    conn = cups.Connection()
    printers = conn.getPrinters()
    if printer_name not in printers:
        raise ValueError(f"Impresora '{printer_name}' no existe en CUPS. Disponibles: {list(printers.keys())}")

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
        f.write(raw_bytes)
        path = Path(f.name)

    try:
        options = {"copies": str(number_of_copies)}
        job_id = conn.printFile(printer_name, str(path), job_title, options)
        logger.info("Trabajo ZPL/raw enviado a %s: job_id=%s, copies=%s", printer_name, job_id, number_of_copies)
        return job_id
    finally:
        path.unlink(missing_ok=True)
