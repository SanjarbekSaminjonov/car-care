from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.telegram.models import TelegramAccount
from services.telegram_account_service import get_telegram_account_for_chat


class TelegramAccountServiceTests(TestCase):
    def test_resolves_account_by_chat_id_and_telegram_user_id(self) -> None:
        first_user = get_user_model().objects.create_user(username="first", password="secret12345")
        second_user = get_user_model().objects.create_user(username="second", password="secret12345")

        matched_account = TelegramAccount.objects.create(
            user=first_user,
            telegram_user_id=101,
            chat_id=999,
        )
        TelegramAccount.objects.create(
            user=second_user,
            telegram_user_id=102,
            chat_id=999,
        )

        resolved_account = get_telegram_account_for_chat(chat_id=999, telegram_user_id=101)

        self.assertEqual(resolved_account.id, matched_account.id)
        self.assertEqual(resolved_account.user_id, first_user.id)

    def test_raises_when_no_account_exists_for_chat_id_and_telegram_user(self) -> None:
        with self.assertRaises(TelegramAccount.DoesNotExist):
            get_telegram_account_for_chat(chat_id=404, telegram_user_id=999)
