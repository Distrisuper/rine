"""Interfaz para parsear extra_data del ítem de cola. Permite inyectar implementación real o mock."""
from abc import ABC, abstractmethod

from domain.entities.models import ExtraDataRemito


class ExtraDataParser(ABC):
    """Contrato para parsear el JSON de QueueItem.extra_data."""

    @abstractmethod
    def parse(self, raw: str | None) -> ExtraDataRemito | None:
        """Parsea extra_data; devuelve None si está vacío o es inválido."""
        pass
