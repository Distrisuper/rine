"""Interfaz para renderizar remito (template + datos → PDF)."""
from abc import ABC, abstractmethod

from domain.value_objects import RemitoRenderData


class RemitoRenderer(ABC):
    """Contrato para generar PDF de remito."""

    @abstractmethod
    def render(self, template_id: str, data: RemitoRenderData) -> bytes:
        """Genera el PDF del remito."""
        pass
