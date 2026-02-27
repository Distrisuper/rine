"""Interfaz para obtener datos completos de remito (desde ítem + extra o API)."""
from abc import ABC, abstractmethod

from domain.entities.models import ExtraDataRemito, QueueItem, RemitoRenderData


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


class InlineRemitoDataProvider(RemitoDataProvider):
    """Implementación que usa datos inline del ítem."""

    def get_render_data(
        self,
        item: QueueItem,
        extra: ExtraDataRemito | None,
    ) -> RemitoRenderData:
        return RemitoRenderData(
            client_code=item.client_code or "",
            client_name=item.client_name or "",
            order_number=getattr(item, "order_number", 0) or 0,
            address=getattr(item, "address", "") or "",
            city=getattr(item, "city", "") or "",
            items=[],
            total=0.0,
            remito_id=getattr(item, "remito_id", "") or "",
            fecha="",
        )
