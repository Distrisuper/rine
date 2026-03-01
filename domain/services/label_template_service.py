"""Orquestador rótulo: parse → resolver → data provider → render → ZPL."""
from domain.value_objects import ExtraDataRemito, LabelRenderData, QueueItem
from domain.services.label_renderer import LabelRenderer
from domain.services.label_template_resolver import LabelTemplateResolver

class LabelTemplateService:
    """Genera ZPL de etiqueta para un ítem de cola (channel 3)."""

    def __init__(
        self,
        resolver: LabelTemplateResolver,
        renderer: LabelRenderer,
    ):
        self._resolver = resolver
        self._renderer = renderer

    def render(self, item: QueueItem) -> bytes:
        """Devuelve el ZPL de la etiqueta para el ítem."""
        extra = ExtraDataRemito.from_json(item.extra_data)
        resolved = self._resolver.resolve(channel=item.channel, location=item.location or "")
        
        if not resolved:
            raise ValueError(f"Ítem no es etiqueta imprimible (channel={item.channel})")
            
        data = LabelRenderData.from_queue_item(item, extra)
        return self._renderer.render(resolved.template_id, data)
