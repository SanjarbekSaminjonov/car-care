from django.db import connection
from django.http import JsonResponse
from django.views import View


class HealthCheckView(View):
    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):  # type: ignore[override]
        return JsonResponse({"status": "ok"})


class ReadinessCheckView(View):
    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):  # type: ignore[override]
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        except Exception:  # noqa: BLE001
            return JsonResponse({"status": "error", "database": "unavailable"}, status=503)

        return JsonResponse({"status": "ok", "database": "ok"})
