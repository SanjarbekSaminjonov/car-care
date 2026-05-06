from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.telegram.models import TelegramAccount
from services.telegram_account_service import get_telegram_account_for_chat, sync_telegram_account


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

    def test_sync_creates_user_and_telegram_account(self) -> None:
        account = sync_telegram_account(
            chat_id=777,
            telegram_user_id=505,
            username="driver_505",
            first_name="Driver",
            last_name="One",
            language_code="uz",
        )

        self.assertEqual(account.user.username, "tg_505")
        self.assertEqual(account.chat_id, 777)
        self.assertEqual(account.username, "driver_505")
        self.assertEqual(account.first_name, "Driver")
        self.assertEqual(account.language_code, "uz")
        self.assertIsNotNone(account.last_seen_at)

    def test_sync_updates_existing_account(self) -> None:
        account = sync_telegram_account(chat_id=1, telegram_user_id=909, username="old")

        updated = sync_telegram_account(
            chat_id=2,
            telegram_user_id=909,
            username="new",
            first_name="New",
        )

        self.assertEqual(updated.id, account.id)
        self.assertEqual(updated.user_id, account.user_id)
        self.assertEqual(updated.chat_id, 2)
        self.assertEqual(updated.username, "new")
        self.assertEqual(updated.first_name, "New")

    def test_blocked_account_is_not_resolved_for_actions(self) -> None:
        user = get_user_model().objects.create_user(username="blocked", password="secret12345")
        TelegramAccount.objects.create(
            user=user,
            telegram_user_id=303,
            chat_id=333,
            is_blocked=True,
        )

        with self.assertRaises(TelegramAccount.DoesNotExist):
            get_telegram_account_for_chat(chat_id=333, telegram_user_id=303)
