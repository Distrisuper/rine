"""Interfaz para renderizar etiqueta/rótulo (template + datos → ZPL)."""
from abc import ABC, abstractmethod

from app.models import LabelRenderData


class LabelRenderer(ABC):
    """Contrato para generar ZPL de etiqueta."""

    @abstractmethod
    def render(self, template_id: str, data: LabelRenderData) -> bytes:
        """Genera el ZPL de la etiqueta."""
        pass
