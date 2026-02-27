"""Interfaz para obtener datos de etiqueta/rótulo a partir del ítem."""
from abc import ABC, abstractmethod

from domain.entities.models import ExtraDataRemito, LabelRenderData, QueueItem


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


class InlineLabelDataProvider(LabelDataProvider):
    """Implementación que usa datos inline del ítem."""

    def get_render_data(
        self,
        item: QueueItem,
        extra: ExtraDataRemito | None,
    ) -> LabelRenderData:
        return LabelRenderData(
            to=item.client_name or "",
            address=getattr(item, "address", "") or "",
            city=getattr(item, "city", "") or "",
            packages=str(item.quantity) if hasattr(item, "quantity") and item.quantity else "",
        )
