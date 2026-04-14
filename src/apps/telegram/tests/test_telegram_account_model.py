from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from apps.telegram.models import TelegramAccount


class TelegramAccountModelTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="demo-user",
            password="secret12345",
        )

    def test_creates_telegram_account_for_user(self) -> None:
        account = TelegramAccount.objects.create(
            user=self.user,
            telegram_user_id=123456789,
            chat_id=987654321,
            username="demo_telegram",
        )

        self.assertEqual(account.user, self.user)
        self.assertEqual(str(account), "@demo_telegram")

    def test_telegram_user_id_is_unique(self) -> None:
        TelegramAccount.objects.create(
            user=self.user,
            telegram_user_id=123456789,
            chat_id=111,
        )

        second_user = get_user_model().objects.create_user(
            username="another-user",
            password="secret12345",
        )

        with self.assertRaises(IntegrityError):
            TelegramAccount.objects.create(
                user=second_user,
                telegram_user_id=123456789,
                chat_id=222,
            )
