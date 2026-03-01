"""Interfaz para resolver el template de remito según channel y contexto (legacy: server, ds, location)."""
from abc import ABC, abstractmethod

from domain.value_objects import ResolvedTemplate


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


class LegacyRemitoTemplateResolver(RemitoTemplateResolver):
    """Implementación legacy que retorna un template por defecto."""

    def resolve(
        self,
        channel: int,
        location: str,
        server: str | None = None,
        ds: str | None = None,
    ) -> ResolvedTemplate | None:
        if channel in (4, 8):
            return ResolvedTemplate(template_id="remito_default", output_type="pdf")
        return None
