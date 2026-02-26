"""Interfaz para descubrimiento y estado de impresoras. Permite inyectar CUPS, mock o tests."""
from abc import ABC, abstractmethod
from typing import Any


class PrinterDiscovery(ABC):
    """Contrato para obtener estado de la flota de impresoras."""

    @abstractmethod
    def get_flota_status(self) -> dict[str, Any]:
        """Estado de todas las impresoras. Incluye 'printers' y opcionalmente '_cups_unavailable' o '_mock'."""
        pass

    @abstractmethod
    def get_printer_status(self, name: str) -> dict[str, Any] | None:
        """Estado de una impresora por nombre. None si no existe o no disponible."""
        pass

    @abstractmethod
    def discover_printers(self) -> list[dict[str, Any]]:
        """Lista impresoras descubiertas con nombre, modelo y tipo detectado (zebra/laser)."""
        pass
