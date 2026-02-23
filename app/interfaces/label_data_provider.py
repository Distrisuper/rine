"""Interfaz para obtener datos de etiqueta/rótulo a partir del ítem."""
from abc import ABC, abstractmethod

from app.models import ExtraDataRemito, LabelRenderData, QueueItem


class LabelDataProvider(ABC):
    """Contrato para armar LabelRenderData a partir del ítem y extra_data."""

    @abstractmethod
    def get_render_data(
        self,
        item: QueueItem,
        extra: ExtraDataRemito | None,
    ) -> LabelRenderData:
        """Construye los datos necesarios para renderizar la etiqueta."""
        pass
