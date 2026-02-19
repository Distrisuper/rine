"""Interfaz para obtener datos completos de remito (desde ítem + extra o API)."""
from abc import ABC, abstractmethod

from app.models import ExtraDataRemito, QueueItem, RemitoRenderData


class RemitoDataProvider(ABC):
    """Contrato para armar RemitoRenderData a partir del ítem y extra_data."""

    @abstractmethod
    def get_render_data(
        self,
        item: QueueItem,
        extra: ExtraDataRemito | None,
    ) -> RemitoRenderData:
        """Construye los datos necesarios para renderizar el remito."""
        pass
