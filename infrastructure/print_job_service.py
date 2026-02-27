"""
Envío de trabajos de impresión a CUPS.
Solo funciona en Linux con CUPS y pycups; en Windows no hay envío real.
"""
import logging
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    import cups
    CUPS_AVAILABLE = True
except ImportError:
    CUPS_AVAILABLE = False
    cups = None


def print_pdf_to_printer(printer_name: str, pdf_bytes: bytes, job_title: str = "Remito") -> int:
    """
    Envía un PDF a una cola CUPS por nombre.
    Requiere Linux con CUPS y la impresora ya configurada en CUPS.

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
        job_id = conn.printFile(printer_name, str(path), job_title, {})
        logger.info("Trabajo enviado a %s: job_id=%s", printer_name, job_id)
        return job_id
    finally:
        path.unlink(missing_ok=True)


def print_raw_to_printer(
    printer_name: str,
    raw_bytes: bytes,
    job_title: str = "Etiqueta",
    suffix: str = ".zpl",
) -> int:
    """
    Envía datos en bruto (ej. ZPL) a una cola CUPS por nombre.
    Pensado para impresoras de etiquetas (Zebra) configuradas con cola raw (-m raw).

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
        job_id = conn.printFile(printer_name, str(path), job_title, {})
        logger.info("Trabajo ZPL/raw enviado a %s: job_id=%s", printer_name, job_id)
        return job_id
    finally:
        path.unlink(missing_ok=True)
