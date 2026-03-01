"""Interfaz para resolver el template de etiqueta/rótulo según channel."""
from abc import ABC, abstractmethod

from domain.value_objects import ResolvedTemplate


class LabelTemplateResolver(ABC):
    """Contrato para obtener el template_id de etiqueta (channel 3)."""

    @abstractmethod
    def resolve(self, channel: int, location: str = "") -> ResolvedTemplate | None:
        """Devuelve el template para rótulo (channel 3) o None si no aplica."""
        pass


class LegacyLabelTemplateResolver(LabelTemplateResolver):
    """Implementación legacy que retorna un template por defecto."""

    def resolve(self, channel: int, location: str = "") -> ResolvedTemplate | None:
        if channel == 3:
            return ResolvedTemplate(template_id="label_default", output_type="zpl")
        return None
