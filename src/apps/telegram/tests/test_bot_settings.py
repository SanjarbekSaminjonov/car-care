import os
from unittest import mock

from django.test import SimpleTestCase

from bot.config.settings import BotSettingsError, get_required_telegram_token


class BotSettingsTests(SimpleTestCase):
    def test_get_required_telegram_token_returns_value(self) -> None:
        with mock.patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "token-123"}, clear=False):
            self.assertEqual(get_required_telegram_token(), "token-123")

    def test_get_required_telegram_token_raises_when_missing(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(BotSettingsError):
                get_required_telegram_token()
