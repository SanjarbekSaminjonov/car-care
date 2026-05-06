from django.test import SimpleTestCase, TestCase


class HealthCheckTests(SimpleTestCase):
    def test_healthcheck_returns_ok_json(self) -> None:
        response = self.client.get("/health/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})


class ReadinessCheckTests(TestCase):
    def test_readiness_returns_ok_when_database_is_available(self) -> None:
        response = self.client.get("/ready/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok", "database": "ok"})
