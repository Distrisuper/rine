"""Tests del parser de extra_data y del modelo ExtraDataRemito."""
import unittest
from app.models import ExtraDataRemito
from app.services.extra_data_parser import DefaultExtraDataParser


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


class TestDefaultExtraDataParser(unittest.TestCase):
    def setUp(self):
        self.parser = DefaultExtraDataParser()

    def test_parse_delegates_to_model(self):
        raw = '{"label_to": "Test"}'
        result = self.parser.parse(raw)
        self.assertIsNotNone(result)
        self.assertEqual(result.label_to, "Test")

    def test_parse_none_returns_none(self):
        self.assertIsNone(self.parser.parse(None))
