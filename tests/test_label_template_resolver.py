"""Tests del resolver de template de etiqueta (channel 3)."""
import unittest
from app.services.label_template_resolver import LegacyLabelTemplateResolver


class TestLegacyLabelTemplateResolver(unittest.TestCase):
    def setUp(self):
        self.resolver = LegacyLabelTemplateResolver()

    def test_channel_3_returns_zpl_template(self):
        r = self.resolver.resolve(3, "MDP")
        self.assertIsNotNone(r)
        self.assertEqual(r.output_type, "zpl")
        self.assertEqual(r.template_id, "etiqueta_standard")

    def test_channel_1_returns_none(self):
        self.assertIsNone(self.resolver.resolve(1))
        self.assertIsNone(self.resolver.resolve(4))
        self.assertIsNone(self.resolver.resolve(8))
