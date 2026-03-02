"""Orquestador rótulo: parse → data provider → render → ZPL."""
from domain.value_objects import ExtraDataRemito, LabelRenderData, QueueItem
from domain.services.label_renderer_interface import LabelRenderer

class LabelTemplateService:
    """Genera ZPL de etiqueta para un ítem de cola."""

    def __init__(self, renderer: LabelRenderer):
        self._renderer = renderer

    def render(self, item: QueueItem, template_path: str) -> bytes:
        """Devuelve el ZPL de la etiqueta para el ítem."""
        extra = ExtraDataRemito.from_json(item.extra_data)
        data = LabelRenderData.from_queue_item(item, extra)
        return self._renderer.render(template_path, data)
