"""Orquestador remito: parse → resolver → data provider → render → PDF."""
from domain.value_objects import ExtraDataRemito, RemitoRenderData, QueueItem
from domain.services.remito_renderer import RemitoRenderer
from domain.services.remito_template_resolver import RemitoTemplateResolver

class RemitoTemplateService:
    """Genera PDF de remito para un ítem de cola (channels 4 u 8)."""

    def __init__(
        self,
        resolver: RemitoTemplateResolver,
        renderer: RemitoRenderer,
    ):
        self._resolver = resolver
        self._renderer = renderer

    def render(self, item: QueueItem) -> bytes:
        """Devuelve el PDF del remito para el ítem."""
        extra = ExtraDataRemito.from_json(item.extra_data)
        resolved = self._resolver.resolve(channel=item.channel, location=item.location or "")
        
        if not resolved:
            raise ValueError(f"Ítem no es remito imprimible (channel={item.channel})")
            
        data = RemitoRenderData.from_queue_item(item, extra)
        return self._renderer.render(resolved.template_id, data)
