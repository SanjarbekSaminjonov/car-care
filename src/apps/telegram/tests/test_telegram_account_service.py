from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.telegram.models import TelegramAccount
from services.telegram_account_service import get_telegram_account_for_chat


class TelegramAccountServiceTests(TestCase):
    def test_returns_most_recent_account_when_chat_id_has_duplicates(self) -> None:
        first_user = get_user_model().objects.create_user(username="first", password="secret12345")
        second_user = get_user_model().objects.create_user(username="second", password="secret12345")

        TelegramAccount.objects.create(
            user=first_user,
            telegram_user_id=101,
            chat_id=999,
        )
        latest_account = TelegramAccount.objects.create(
            user=second_user,
            telegram_user_id=102,
            chat_id=999,
        )

        resolved_account = get_telegram_account_for_chat(chat_id=999)

        self.assertEqual(resolved_account.id, latest_account.id)
        self.assertEqual(resolved_account.user_id, second_user.id)

    def test_raises_when_no_account_exists_for_chat_id(self) -> None:
        with self.assertRaises(TelegramAccount.DoesNotExist):
            get_telegram_account_for_chat(chat_id=404)
