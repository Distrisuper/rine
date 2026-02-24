"""Tests del orquestador de rótulo (parser + resolver + provider + renderer)."""
import unittest
from unittest.mock import MagicMock

from domain.entities.models import ExtraDataRemito, LabelRenderData, QueueItem, ResolvedTemplate
from domain.services.label_template_service import LabelTemplateService


def _label_item(channel: int = 3, location: str = "MDP", extra_data: str | None = None):
    return QueueItem(
        id=2,
        client_id="c2",
        client_code="",
        client_name="Destino",
        order_number=200,
        type="etiqueta",
        type_code=None,
        location=location,
        channel=channel,
        invoice_type=None,
        invoice_number=None,
        invoice_comment="",
        invoice_total=None,
        result=0,
        result_detail="",
        retry=0,
        priority=0,
        printed=0,
        print_count=1,
        host=1,
        redi_code="",
        redi_id=0,
        date_created="2025-01-01",
        date_started=None,
        date_processed=None,
        extra_data=extra_data,
    )


class TestLabelTemplateService(unittest.TestCase):
    def setUp(self):
        self.parser = MagicMock()
        self.resolver = MagicMock()
        self.data_provider = MagicMock()
        self.renderer = MagicMock()
        self.service = LabelTemplateService(
            parser=self.parser,
            resolver=self.resolver,
            data_provider=self.data_provider,
            renderer=self.renderer,
        )

    def test_render_calls_parser_resolver_provider_renderer(self):
        item = _label_item(extra_data='{"label_to": "Juan", "label_city": "MDP"}')
        self.parser.parse.return_value = ExtraDataRemito(
            label_to="Juan", label_city="MDP"
        )
        self.resolver.resolve.return_value = ResolvedTemplate(
            template_id="etiqueta_standard", output_type="zpl"
        )
        data = LabelRenderData(to="Juan", city="MDP")
        self.data_provider.get_render_data.return_value = data
        self.renderer.render.return_value = b"^XA^FO50,50^FDJuan^FS^XZ"

        result = self.service.render(item)

        self.parser.parse.assert_called_once_with(item.extra_data)
        self.resolver.resolve.assert_called_once()
        self.data_provider.get_render_data.assert_called_once_with(
            item, self.parser.parse.return_value
        )
        self.renderer.render.assert_called_once_with("etiqueta_standard", data)
        self.assertEqual(result, b"^XA^FO50,50^FDJuan^FS^XZ")

    def test_render_raises_when_resolver_returns_none(self):
        item = _label_item(channel=1)
        self.resolver.resolve.return_value = None

        with self.assertRaises(ValueError) as ctx:
            self.service.render(item)
        self.assertIn("channel=1", str(ctx.exception))
