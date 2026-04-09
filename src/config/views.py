from django.http import JsonResponse
from django.views import View


class HealthCheckView(View):
    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):  # type: ignore[override]
        return JsonResponse({"status": "ok"})
