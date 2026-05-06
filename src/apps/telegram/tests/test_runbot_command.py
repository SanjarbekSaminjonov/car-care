import os
from io import StringIO
from unittest import mock

from django.core.management import CommandError, call_command
from django.test import SimpleTestCase, TestCase

from bot.handlers.commands import BotReply


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


class RunBotCommandIdempotencyTests(TestCase):
    def test_runbot_does_not_send_reply_for_duplicate_update(self) -> None:
        output = StringIO()
        update = {"update_id": 8801, "message": {"chat": {"id": 9901}, "text": "/start"}}

        with mock.patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "token-123"}, clear=False):
            with mock.patch(
                "apps.telegram.management.commands.runbot.TelegramBotClient.get_updates",
                side_effect=([update], [update], KeyboardInterrupt),
            ):
                with mock.patch(
                    "apps.telegram.management.commands.runbot.TelegramBotClient.send_message"
                ) as send_message:
                    call_command("runbot", stdout=output, poll_timeout=1, sleep_seconds=0)

        self.assertEqual(send_message.call_count, 1)

    def test_runbot_answers_callback_query(self) -> None:
        output = StringIO()
        calls: list[str] = []
        update = {
            "update_id": 8802,
            "callback_query": {
                "id": "callback-1",
                "from": {"id": 8001},
                "message": {"chat": {"id": 9902}},
                "data": "odometer:confirm",
            },
        }

        with mock.patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "token-123"}, clear=False):
            with mock.patch(
                "apps.telegram.management.commands.runbot.TelegramBotClient.get_updates",
                side_effect=([update], KeyboardInterrupt),
            ) as get_updates:
                with (
                    mock.patch(
                        "apps.telegram.management.commands.runbot.UpdateDispatcher.dispatch",
                        side_effect=lambda _update: calls.append("dispatch") or BotReply(chat_id=9902, text="OK"),
                    ),
                    mock.patch(
                        "apps.telegram.management.commands.runbot.TelegramBotClient.answer_callback_query",
                        side_effect=lambda **_kwargs: calls.append("answer"),
                    ) as answer_callback_query,
                    mock.patch(
                        "apps.telegram.management.commands.runbot.TelegramBotClient.send_message"
                    ) as send_message,
                ):
                    call_command("runbot", stdout=output, poll_timeout=1, sleep_seconds=0)

        get_updates.assert_any_call(
            offset=None,
            timeout=1,
            allowed_updates=["message", "callback_query"],
        )
        answer_callback_query.assert_called_once_with(callback_query_id="callback-1")
        self.assertEqual(calls, ["answer", "dispatch"])
        send_message.assert_called_once()

    def test_runbot_dispatches_callback_even_when_answer_fails(self) -> None:
        output = StringIO()
        update = {
            "update_id": 8803,
            "callback_query": {
                "id": "callback-2",
                "from": {"id": 8002},
                "message": {"chat": {"id": 9903}},
                "data": "odometer:confirm",
            },
        }

        with mock.patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "token-123"}, clear=False):
            with mock.patch(
                "apps.telegram.management.commands.runbot.TelegramBotClient.get_updates",
                side_effect=([update], KeyboardInterrupt),
            ):
                with (
                    mock.patch(
                        "apps.telegram.management.commands.runbot.UpdateDispatcher.dispatch",
                        return_value=BotReply(chat_id=9903, text="OK"),
                    ) as dispatch,
                    mock.patch(
                        "apps.telegram.management.commands.runbot.TelegramBotClient.answer_callback_query",
                        side_effect=RuntimeError("expired"),
                    ),
                    mock.patch("apps.telegram.management.commands.runbot.TelegramBotClient.send_message"),
                ):
                    call_command("runbot", stdout=output, poll_timeout=1, sleep_seconds=0)

        dispatch.assert_called_once_with(update)
