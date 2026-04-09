from django.test import SimpleTestCase


class HealthCheckTests(SimpleTestCase):
    def test_healthcheck_returns_ok_json(self) -> None:
        response = self.client.get("/health/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})
