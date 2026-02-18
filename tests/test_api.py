# Test API (mínimo)

class TestAPI(unittest.TestCase):
	def setUp(self):
		self.client = TestClient(app)

	def test_hello_endpoint(self):
		response = self.client.get("/")
		self.assertEqual(response.status_code, 200)
		self.assertIn("message", response.json())

	def test_health_endpoint(self):
		response = self.client.get("/health")
		self.assertEqual(response.status_code, 200)
		self.assertIn("status", response.json())

if __name__ == "__main__":
	unittest.main()
