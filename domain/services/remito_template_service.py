"""Orquestador remito: parse → data provider → render → PDF."""
from domain.value_objects import ExtraDataRemito, RemitoRenderData, QueueItem
from domain.services.remito_renderer_interface import RemitoRenderer

class RemitoTemplateService:
    """Genera PDF de remito para un ítem de cola."""

    def __init__(self, renderer: RemitoRenderer):
        self._renderer = renderer

    def render(self, item: QueueItem, template_path: str) -> bytes:
        """Devuelve el PDF del remito para el ítem."""
        extra = ExtraDataRemito.from_json(item.extra_data)
        data = RemitoRenderData.from_queue_item(item, extra)
        return self._renderer.render(template_path, data)
