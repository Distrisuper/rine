"""Tests del resolver de template de remito (reglas legacy)."""
import unittest
from domain.services.remito_template_resolver import LegacyRemitoTemplateResolver


class TestLegacyRemitoTemplateResolver(unittest.TestCase):
    def setUp(self):
        self.resolver = LegacyRemitoTemplateResolver()

    def test_channel_4_returns_resolved(self):
        r = self.resolver.resolve(4, "MDP", server="0", ds="remito")
        self.assertIsNotNone(r)
        self.assertEqual(r.output_type, "pdf")
        self.assertEqual(r.template_id, "templateremnooficialMDP")

    def test_channel_8_returns_resolved(self):
        r = self.resolver.resolve(8, "BA", ds="remito")
        self.assertIsNotNone(r)
        self.assertEqual(r.template_id, "templateremnooficialBA")

    def test_channel_1_returns_none(self):
        self.assertIsNone(self.resolver.resolve(1, "MDP"))
        self.assertIsNone(self.resolver.resolve(3, "ROS"))

    def test_ds_remito_sucursales(self):
        self.assertEqual(
            self.resolver.resolve(4, "MDP", ds="remito").template_id,
            "templateremnooficialMDP",
        )
        self.assertEqual(
            self.resolver.resolve(4, "ROS", ds="remito").template_id,
            "templateremnooficialROS",
        )
        self.assertEqual(
            self.resolver.resolve(4, "PICO", ds="remito").template_id,
            "templateremnooficialPICO",
        )

    def test_ds_1_returns_templateds(self):
        r = self.resolver.resolve(4, "X", ds="1")
        self.assertIsNotNone(r)
        self.assertEqual(r.template_id, "templateds")

    def test_ros_without_ds_returns_templateros(self):
        r = self.resolver.resolve(4, "ROS")
        self.assertIsNotNone(r)
        self.assertEqual(r.template_id, "templateros")

    def test_server_1_returns_template(self):
        r = self.resolver.resolve(4, "BA", server="1")
        self.assertEqual(r.template_id, "template")

    def test_default_returns_templatedimes(self):
        r = self.resolver.resolve(4, "BA", server="0")
        self.assertEqual(r.template_id, "templatedimes")
