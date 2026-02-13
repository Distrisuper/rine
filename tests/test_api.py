"""
Tests for API endpoints.
"""
import unittest
from fastapi.testclient import TestClient
from app.main import app

class TestAPI(unittest.TestCase):
	def setUp(self):
		self.client = TestClient(app)

	def test_hello_endpoint(self):
		response = self.client.get("/hello")
		self.assertEqual(response.status_code, 200)
		self.assertIn("message", response.json())

	def test_queue_endpoint(self):
		response = self.client.get("/queue/status")
		self.assertEqual(response.status_code, 200)
		self.assertIn("status", response.json())

if __name__ == "__main__":
	unittest.main()
