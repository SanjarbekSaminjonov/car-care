import importlib
import os
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class SettingsSmokeTests(SimpleTestCase):
    def test_custom_user_model_is_configured(self) -> None:
        self.assertEqual(settings.AUTH_USER_MODEL, "users.User")

    def test_users_app_is_installed(self) -> None:
        self.assertIn("apps.users.apps.UsersConfig", settings.INSTALLED_APPS)

    def test_telegram_app_is_installed(self) -> None:
        self.assertIn("apps.telegram.apps.TelegramConfig", settings.INSTALLED_APPS)

    def test_core_domain_apps_are_installed(self) -> None:
        self.assertIn("apps.cars.apps.CarsConfig", settings.INSTALLED_APPS)
        self.assertIn("apps.odometer.apps.OdometerConfig", settings.INSTALLED_APPS)
        self.assertIn("apps.maintenance.apps.MaintenanceConfig", settings.INSTALLED_APPS)
        self.assertIn("apps.assistant.apps.AssistantConfig", settings.INSTALLED_APPS)
        self.assertIn("apps.audit.apps.AuditConfig", settings.INSTALLED_APPS)
        self.assertIn("apps.notifications.apps.NotificationsConfig", settings.INSTALLED_APPS)

    def test_default_database_engine_is_postgresql(self) -> None:
        self.assertEqual(
            settings.DATABASES["default"]["ENGINE"], "django.db.backends.postgresql"
        )

    def test_runtime_paths_are_outside_src(self) -> None:
        self.assertEqual(settings.MEDIA_ROOT, Path(settings.ROOT_DIR) / "var" / "media")
        self.assertEqual(settings.STATIC_ROOT, Path(settings.ROOT_DIR) / "var" / "static")

    def test_production_settings_module_is_importable(self) -> None:
        original_allowed_hosts = os.environ.get("DJANGO_ALLOWED_HOSTS")
        original_csrf = os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS")
        original_secret_key = os.environ.get("DJANGO_SECRET_KEY")
        original_postgres_db = os.environ.get("POSTGRES_DB")
        original_postgres_user = os.environ.get("POSTGRES_USER")
        original_postgres_password = os.environ.get("POSTGRES_PASSWORD")
        original_postgres_host = os.environ.get("POSTGRES_HOST")
        original_postgres_port = os.environ.get("POSTGRES_PORT")
        os.environ["DJANGO_ALLOWED_HOSTS"] = "carcare.example.com"
        os.environ["DJANGO_CSRF_TRUSTED_ORIGINS"] = "https://carcare.example.com"
        os.environ["DJANGO_SECRET_KEY"] = "test-production-secret"
        os.environ["POSTGRES_DB"] = "car_care"
        os.environ["POSTGRES_USER"] = "car_care"
        os.environ["POSTGRES_PASSWORD"] = "car_care"
        os.environ["POSTGRES_HOST"] = "localhost"
        os.environ["POSTGRES_PORT"] = "5432"
        try:
            module = importlib.import_module("config.settings.production")
        finally:
            if original_allowed_hosts is None:
                os.environ.pop("DJANGO_ALLOWED_HOSTS", None)
            else:
                os.environ["DJANGO_ALLOWED_HOSTS"] = original_allowed_hosts

            if original_csrf is None:
                os.environ.pop("DJANGO_CSRF_TRUSTED_ORIGINS", None)
            else:
                os.environ["DJANGO_CSRF_TRUSTED_ORIGINS"] = original_csrf
            if original_secret_key is None:
                os.environ.pop("DJANGO_SECRET_KEY", None)
            else:
                os.environ["DJANGO_SECRET_KEY"] = original_secret_key
            if original_postgres_db is None:
                os.environ.pop("POSTGRES_DB", None)
            else:
                os.environ["POSTGRES_DB"] = original_postgres_db
            if original_postgres_user is None:
                os.environ.pop("POSTGRES_USER", None)
            else:
                os.environ["POSTGRES_USER"] = original_postgres_user
            if original_postgres_password is None:
                os.environ.pop("POSTGRES_PASSWORD", None)
            else:
                os.environ["POSTGRES_PASSWORD"] = original_postgres_password
            if original_postgres_host is None:
                os.environ.pop("POSTGRES_HOST", None)
            else:
                os.environ["POSTGRES_HOST"] = original_postgres_host
            if original_postgres_port is None:
                os.environ.pop("POSTGRES_PORT", None)
            else:
                os.environ["POSTGRES_PORT"] = original_postgres_port

        self.assertFalse(module.DEBUG)
