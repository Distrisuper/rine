"""Tests de integración para endpoints de prueba de templates (remito / etiqueta)."""
import base64
import unittest
from fastapi.testclient import TestClient
from app.main import app


class TestTemplatesRemitoAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_remito_test_returns_pdf(self):
        body = {
            "channel": 4,
            "location": "MDP",
            "ds": "remito",
            "client_name": "Cliente SA",
            "extra_data": '{"idRemito": "R-001", "label_city": "Mar del Plata", "label_address": "Av. 1 123"}',
        }
        response = self.client.post("/queue/templates/remito/test", json=body)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("content-type"), "application/pdf")
        self.assertGreater(len(response.content), 0)
        self.assertTrue(response.content.startswith(b"%PDF"), "Debe ser un PDF válido")

    def test_remito_test_format_json_returns_base64(self):
        body = {"channel": 4, "location": "MDP", "ds": "remito"}
        response = self.client.post(
            "/queue/templates/remito/test", json=body, params={"format": "json"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("content_base64", data)
        self.assertIn("size", data)
        self.assertEqual(data["content_type"], "application/pdf")
        decoded = base64.b64decode(data["content_base64"])
        self.assertTrue(decoded.startswith(b"%PDF"))

    def test_remito_test_invalid_channel_returns_400(self):
        body = {"channel": 1, "location": "MDP"}
        response = self.client.post("/queue/templates/remito/test", json=body)
        self.assertEqual(response.status_code, 400)


class TestTemplatesLabelAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_label_test_returns_zpl(self):
        body = {
            "channel": 3,
            "location": "MDP",
            "extra_data": '{"label_to": "Juan", "label_address": "Calle 50", "label_city": "MDP"}',
        }
        response = self.client.post("/queue/templates/label/test", json=body)
        self.assertEqual(response.status_code, 200)
        self.assertIn("zpl", response.headers.get("content-type", ""))
        self.assertGreater(len(response.content), 0)
        self.assertIn(b"^XA", response.content)
        self.assertIn(b"^XZ", response.content)

    def test_label_test_format_json_returns_preview(self):
        body = {"channel": 3, "location": "MDP"}
        response = self.client.post(
            "/queue/templates/label/test", json=body, params={"format": "json"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("content_preview", data)
        self.assertIn("^XA", data["content_preview"])

    def test_label_test_invalid_channel_returns_400(self):
        body = {"channel": 4, "location": "MDP"}
        response = self.client.post("/queue/templates/label/test", json=body)
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
