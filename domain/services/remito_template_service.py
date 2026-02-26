"""Orquestador remito: parse → resolver → data provider → render → PDF."""
from domain.services.extra_data_parser_interface import ExtraDataParser
from domain.repositories.remito_data_provider import RemitoDataProvider
from domain.repositories.remito_renderer import RemitoRenderer
from domain.repositories.remito_template_resolver import RemitoTemplateResolver
from domain.entities.models import QueueItem


class RemitoTemplateService:
    """Genera PDF de remito para un ítem de cola (channel 4 u 8)."""

    def __init__(
        self,
        parser: ExtraDataParser,
        resolver: RemitoTemplateResolver,
        data_provider: RemitoDataProvider,
        renderer: RemitoRenderer,
    ):
        self._parser = parser
        self._resolver = resolver
        self._data_provider = data_provider
        self._renderer = renderer

    def render(self, item: QueueItem) -> bytes:
        """Devuelve el PDF del remito para el ítem."""
        extra = self._parser.parse(item.extra_data)
        resolved = self._resolver.resolve(
            channel=item.channel,
            location=item.location or "",
            server=getattr(item, "server", None),
            ds=getattr(item, "ds", None),
        )
        if not resolved:
            raise ValueError(f"Ítem no es remito imprimible (channel={item.channel})")
        data = self._data_provider.get_render_data(item, extra)
        return self._renderer.render(resolved.template_id, data)
