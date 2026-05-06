from django.urls import path

from apps.webapp import views

app_name = "webapp"

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
    path("login/", views.WebAppLoginView.as_view(), name="login"),
    path("auth/telegram/", views.TelegramWebAppAuthView.as_view(), name="telegram_auth"),
    path("maintenance/new/", views.MaintenanceCreateView.as_view(), name="maintenance_create"),
]
