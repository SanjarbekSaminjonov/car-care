from django.contrib import admin
from django.test import SimpleTestCase

from apps.telegram.admin import TelegramAccountAdmin
from apps.telegram.models import TelegramAccount


class TelegramAdminRegistrationTests(SimpleTestCase):
    def test_telegram_account_is_registered_in_admin(self) -> None:
        self.assertIn(TelegramAccount, admin.site._registry)
        self.assertIsInstance(admin.site._registry[TelegramAccount], TelegramAccountAdmin)
