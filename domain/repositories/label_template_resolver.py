"""Interfaz para resolver el template de etiqueta/rótulo según channel."""
from abc import ABC, abstractmethod

from domain.entities.models import ResolvedTemplate


class LabelTemplateResolver(ABC):
    """Contrato para obtener el template_id de etiqueta (channel 3)."""

    @abstractmethod
    def resolve(self, channel: int, location: str = "") -> ResolvedTemplate | None:
        """Devuelve el template para rótulo (channel 3) o None si no aplica."""
        pass
