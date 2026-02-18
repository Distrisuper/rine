"""Controlador para estado de impresoras (monitoreo vía interfaz PrinterDiscovery)."""
from app.interfaces.printer_discovery import PrinterDiscovery


class PrinterController:
    """Estado de la flota de impresoras para testing y monitoreo."""

    @staticmethod
    def get_status(discovery: PrinterDiscovery):
        """Estado de todas las impresoras (ready/not_ready + detalles)."""
        return discovery.get_flota_status()

    @staticmethod
    def get_printer_status(discovery: PrinterDiscovery, name: str):
        """Estado de una impresora por nombre. None si no existe o no disponible."""
        return discovery.get_printer_status(name)
