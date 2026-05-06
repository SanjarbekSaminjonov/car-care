from django.contrib import admin
from django.test import SimpleTestCase

from apps.telegram.admin import ProcessedTelegramUpdateAdmin, TelegramAccountAdmin
from apps.telegram.models import ProcessedTelegramUpdate, TelegramAccount


class TelegramAdminRegistrationTests(SimpleTestCase):
    def test_telegram_account_is_registered_in_admin(self) -> None:
        self.assertIn(TelegramAccount, admin.site._registry)
        self.assertIsInstance(admin.site._registry[TelegramAccount], TelegramAccountAdmin)

    def test_processed_telegram_update_is_registered_in_admin(self) -> None:
        self.assertIn(ProcessedTelegramUpdate, admin.site._registry)
        self.assertIsInstance(
            admin.site._registry[ProcessedTelegramUpdate],
            ProcessedTelegramUpdateAdmin,
        )
