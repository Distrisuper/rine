"""Construye RemitoRenderData desde QueueItem y ExtraDataRemito (sin API externa por ahora)."""
from app.interfaces.remito_data_provider import RemitoDataProvider
from app.models import ExtraDataRemito, QueueItem, RemitoRenderData


class InlineRemitoDataProvider(RemitoDataProvider):
    """Armado de datos solo desde ítem y extra_data; sin llamadas a API."""

    def get_render_data(
        self,
        item: QueueItem,
        extra: ExtraDataRemito | None,
    ) -> RemitoRenderData:
        address = (extra.label_address if extra else None) or ""
        city = (extra.label_city if extra else None) or ""
        remito_id = (
            (extra.idRemito if extra and extra.idRemito else None)
            or (extra.redi_id if extra and extra.redi_id else None)
            or str(getattr(item, "redi_id", ""))
        )
        return RemitoRenderData(
            client_name=item.client_name or "",
            order_number=str(item.order_number),
            address=address,
            city=city,
            items=[],
            total=float(item.invoice_total or 0),
            remito_id=remito_id or "",
        )
