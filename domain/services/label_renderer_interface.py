"""Interfaz para renderizar etiqueta/rótulo (template + datos → ZPL)."""
from abc import ABC, abstractmethod

from domain.value_objects import LabelRenderData


class LabelRenderer(ABC):
    """Contrato para generar ZPL de etiqueta."""

    @abstractmethod
    def render(self, template_id: str, data: LabelRenderData) -> bytes:
        """Genera el ZPL de la etiqueta."""
        pass
