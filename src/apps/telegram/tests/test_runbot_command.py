import os
from io import StringIO
from unittest import mock

from django.core.management import CommandError, call_command
from django.test import SimpleTestCase


class RunBotCommandTests(SimpleTestCase):
    def test_runbot_raises_when_token_missing(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(CommandError):
                call_command("runbot")

    def test_runbot_starts_and_handles_keyboard_interrupt(self) -> None:
        output = StringIO()
        with mock.patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "token-123"}, clear=False):
            with mock.patch(
                "apps.telegram.management.commands.runbot.TelegramBotClient.get_updates",
                side_effect=KeyboardInterrupt,
            ):
                call_command("runbot", stdout=output, poll_timeout=1, sleep_seconds=0)

        rendered = output.getvalue()
        self.assertIn("runbot started", rendered)
        self.assertIn("runbot stopped", rendered)
