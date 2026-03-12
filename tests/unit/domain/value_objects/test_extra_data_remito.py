"""Tests del modelo ExtraDataRemito."""
import unittest
from domain.value_objects import ExtraDataRemito


class TestExtraDataRemitoFromJson(unittest.TestCase):
    def test_none_returns_none(self):
        self.assertIsNone(ExtraDataRemito.from_json(None))

    def test_empty_string_returns_none(self):
        self.assertIsNone(ExtraDataRemito.from_json(""))
        self.assertIsNone(ExtraDataRemito.from_json("   "))

    def test_valid_json_returns_model(self):
        raw = '{"label_to": "Juan", "label_city": "MDP", "idRemito": "R-001"}'
        result = ExtraDataRemito.from_json(raw)
        self.assertIsNotNone(result)
        self.assertEqual(result.label_to, "Juan")
        self.assertEqual(result.label_city, "MDP")
        self.assertEqual(result.idRemito, "R-001")

    def test_invalid_json_returns_none(self):
        self.assertIsNone(ExtraDataRemito.from_json("not json"))
        self.assertIsNone(ExtraDataRemito.from_json("{ invalid }"))

    def test_non_dict_json_returns_none(self):
        self.assertIsNone(ExtraDataRemito.from_json("[]"))
