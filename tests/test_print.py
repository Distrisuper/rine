"""
Tests para endpoints de impresión.
"""
import os
import sqlite3
import unittest
from fastapi.testclient import TestClient
from app.main import app


class TestPrintAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.client.get("/health")

    def _job_count(self) -> int:
        db_path = os.environ.get("SQLITE_DB_PATH", "data/rine.db")
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM print_jobs")
            row = cursor.fetchone()
        return int(row[0])

    def test_print_label(self):
        count_before = self._job_count()
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
        self.assertIn("encolada", data["message"].lower())
        count_after = self._job_count()
        self.assertGreaterEqual(count_after, count_before + 1)

    def test_print_remito(self):
        payload = {
            "type": "REMI",
            "client_code": "CL001",
            "client_name": "Distribuidora ABC",
            "client_address": "Calle Principal 123",
            "client_city": "Buenos Aires",
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
        self.assertIn("encolada", data["message"].lower())

    def test_print_gm_request(self):
        payload = {
            "type": "GM",
            "client_code": "CL001",
            "client_name": "Distribuidora ABC",
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
        self.assertIn("encolada", data["message"].lower())

    def test_print_pending_redi(self):
        payload = {
            "type": "PEND",
            "client_code": "CL001",
            "client_name": "Distribuidora ABC",
            "id_remito": "REM001",
            "redi_code": "REDI001",
            "set_host": 1,
            "package_quantity": 5,
            "pending": 2,
        }
        response = self.client.post("/print", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["ok"], 1)
        self.assertEqual(data["doc_type"], "redi pendiente")
        self.assertIn("encolada", data["message"].lower())

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
        self.assertEqual(response.status_code, 422)
        data = response.json()
        self.assertIsInstance(data.get("detail"), list)
        self.assertTrue(
            any(item.get("loc") == ["body", "type"] for item in data["detail"])
        )

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
