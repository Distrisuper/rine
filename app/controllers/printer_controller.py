"""Controlador para estado de impresoras (monitoreo CUPS)."""
from app.services.printer_discovery_service import monitorear_flota, estado_impresora


class PrinterController:
    """Estado de la flota de impresoras para testing y monitoreo."""

    @staticmethod
    def get_status():
        """Estado de todas las impresoras (ready/not_ready + detalles)."""
        return monitorear_flota()

    @staticmethod
    def get_printer_status(name: str):
        """Estado de una impresora por nombre. None si no existe o CUPS no disponible."""
        return estado_impresora(name)
