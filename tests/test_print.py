"""
Tests para endpoints de impresión.
"""
import unittest
from fastapi.testclient import TestClient
from app.main import app


class TestPrintAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_print_label(self):
        payload = {
            "type": "ETIQ",
            "client_code": "CL001",
            "client_name": "Distribuidora ABC",
            "client_address": "Calle Principal 123",
            "client_city": "Buenos Aires",
            "set_host": 1,
            "package_quantity": 5,
            "redi_code": "REDI001",
            "id_remito": "REM001",
            "label_packages": 10,
        }
        response = self.client.post("/print", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["ok"], 1)
        self.assertEqual(data["doc_type"], "etiqueta")
        self.assertIn("etiqueta", data["message"])

    def test_print_remito(self):
        payload = {
            "type": "REMI",
            "client_code": "CL001",
            "client_name": "Distribuidora ABC",
            "client_address": "Calle Principal 123",
            "client_city": "Buenos Aires",
            "location": "Zona Centro",
            "set_host": 1,
            "remitos_quantity": 3,
            "redi_code": "REDI001",
            "id_remito": "REM001",
            "label_packages": 10,
        }
        response = self.client.post("/print", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["ok"], 1)
        self.assertEqual(data["doc_type"], "remito")

    def test_print_gm_request(self):
        payload = {
            "type": "GM",
            "client_code": "CL001",
            "client_name": "Distribuidora ABC",
            "location": "Zona Centro",
            "id_remito": "REM001",
            "redi_code": "REDI001",
            "set_host": 1,
            "invoices_quantity": 15,
        }
        response = self.client.post("/print", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["ok"], 1)
        self.assertEqual(data["doc_type"], "pedido de impresión")

    def test_print_pending_redi(self):
        payload = {
            "type": "PEND",
            "client_code": "CL001",
            "client_name": "Distribuidora ABC",
            "location": "Zona Centro",
            "id_remito": "REM001",
            "redi_code": "REDI001",
            "set_host": 1,
            "package_quantity": 5,
            "pending": True,
        }
        response = self.client.post("/print", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["ok"], 1)
        self.assertEqual(data["doc_type"], "redi pendiente")

    def test_print_invalid_type(self):
        payload = {
            "type": "INVALID",
            "client_code": "CL001",
            "client_name": "Distribuidora ABC",
            "set_host": 1,
            "redi_code": "REDI001",
            "id_remito": "REM001",
        }
        response = self.client.post("/print", json=payload)
        # Pydantic validation should reject the invalid type before reaching the service,
        # resulting in FastAPI's standard 422 validation error response.
        self.assertEqual(response.status_code, 422)
        detail = response.json()["detail"]
        # 'detail' is a list of error objects; extract their messages and check the enum constraint message.
        messages = " ".join(str(item.get("msg", "")) for item in detail)
        self.assertIn("Input should be 'ETIQ', 'REMI', 'GM' or 'PEND'", messages)

    def test_print_missing_required_fields(self):
        payload = {
            "type": "ETIQ",
            "client_code": "CL001",
            "client_name": "Distribuidora ABC",
            "set_host": 1,
            "redi_code": "REDI001",
            "id_remito": "REM001",
            # Falta client_address, client_city, package_quantity, label_packages
        }
        response = self.client.post("/print", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("requiere", response.json()["detail"])


if __name__ == "__main__":
    unittest.main()
