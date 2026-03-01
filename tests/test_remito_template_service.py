"""Tests del orquestador de remito (resolver + renderer)."""
import unittest
from unittest.mock import MagicMock

from domain.value_objects import ExtraDataRemito, QueueItem, RemitoRenderData, ResolvedTemplate
from domain.services.remito_template_service import RemitoTemplateService


def _remito_item(channel=4, location="MDP", extra_data=None):
    return QueueItem(
        id=1,
        client_id="c1",
        client_code="",
        client_name="Cliente SA",
        order_number=100,
        type="remito",
        type_code=None,
        location=location,
        channel=channel,
        invoice_type=None,
        invoice_number=None,
        invoice_comment="",
        invoice_total=1500.0,
        result=0,
        result_detail="",
        retry=0,
        priority=0,
        printed=0,
        print_count=1,
        host=1,
        redi_code="",
        redi_id=99,
        date_created="2025-01-01",
        date_started=None,
        date_processed=None,
        extra_data=extra_data,
    )


class TestRemitoTemplateService(unittest.TestCase):
    def setUp(self):
        self.resolver = MagicMock()
        self.renderer = MagicMock()
        self.service = RemitoTemplateService(
            resolver=self.resolver,
            renderer=self.renderer,
        )

    def test_render_calls_resolver_and_renderer(self):
        item = _remito_item(extra_data='{"idRemito": "R-1"}')
        self.resolver.resolve.return_value = ResolvedTemplate(
            template_id="templateremnooficialMDP", output_type="pdf"
        )
        self.renderer.render.return_value = b"%PDF-1.4..."

        result = self.service.render(item)

        self.resolver.resolve.assert_called_once()
        self.renderer.render.assert_called_once()
        self.assertEqual(result, b"%PDF-1.4...")

    def test_render_raises_when_resolver_returns_none(self):
        item = _remito_item(channel=1)
        self.resolver.resolve.return_value = None

        with self.assertRaises(ValueError) as ctx:
            self.service.render(item)
        self.assertIn("channel=1", str(ctx.exception))
