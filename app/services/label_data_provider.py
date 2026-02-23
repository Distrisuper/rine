"""Construye LabelRenderData desde QueueItem y ExtraDataRemito."""
from app.interfaces.label_data_provider import LabelDataProvider
from app.models import ExtraDataRemito, LabelRenderData, QueueItem


class InlineLabelDataProvider(LabelDataProvider):
    """Armado de datos de etiqueta solo desde ítem y extra_data."""

    def get_render_data(
        self,
        item: QueueItem,
        extra: ExtraDataRemito | None,
    ) -> LabelRenderData:
        if not extra:
            return LabelRenderData(
                to=item.client_name or "",
                address="",
                city=item.location or "",
                packages="",
                transport="",
                observations="",
            )
        return LabelRenderData(
            to=extra.label_to or item.client_name or "",
            address=extra.label_address or "",
            city=extra.label_city or item.location or "",
            packages=extra.label_packages or "",
            transport=extra.label_transport or "",
            observations="",
        )
