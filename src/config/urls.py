from django.contrib import admin
from django.urls import include, path

from config.views import HealthCheckView, ReadinessCheckView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("app/", include("apps.webapp.urls")),
    path("health/", HealthCheckView.as_view(), name="healthcheck"),
    path("ready/", ReadinessCheckView.as_view(), name="readiness"),
]
