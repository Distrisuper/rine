"""Interfaz para resolver el template de remito según channel y contexto (legacy: server, ds, location)."""
from abc import ABC, abstractmethod

from app.models import ResolvedTemplate


class RemitoTemplateResolver(ABC):
    """Contrato para obtener el template_id de remito según reglas legacy."""

    @abstractmethod
    def resolve(
        self,
        channel: int,
        location: str,
        server: str | None = None,
        ds: str | None = None,
    ) -> ResolvedTemplate | None:
        """Devuelve el template para remito (channel 4 u 8) o None si no aplica."""
        pass
