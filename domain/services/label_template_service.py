"""Orquestador rótulo: parse → resolver → data provider → render → ZPL."""
from domain.services.extra_data_parser_interface import ExtraDataParser
from domain.repositories.label_data_provider import LabelDataProvider
from domain.repositories.label_renderer import LabelRenderer
from domain.repositories.label_template_resolver import LabelTemplateResolver
from domain.entities.models import QueueItem


class LabelTemplateService:
    """Genera ZPL de etiqueta para un ítem de cola (channel 3)."""

    def __init__(
        self,
        parser: ExtraDataParser,
        resolver: LabelTemplateResolver,
        data_provider: LabelDataProvider,
        renderer: LabelRenderer,
    ):
        self._parser = parser
        self._resolver = resolver
        self._data_provider = data_provider
        self._renderer = renderer

    def render(self, item: QueueItem) -> bytes:
        """Devuelve el ZPL de la etiqueta para el ítem."""
        extra = self._parser.parse(item.extra_data)
        resolved = self._resolver.resolve(channel=item.channel, location=item.location or "")
        if not resolved:
            raise ValueError(f"Ítem no es etiqueta imprimible (channel={item.channel})")
        data = self._data_provider.get_render_data(item, extra)
        return self._renderer.render(resolved.template_id, data)
