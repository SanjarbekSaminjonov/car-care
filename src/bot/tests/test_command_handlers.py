from django.test import SimpleTestCase

from bot.handlers.commands import CommandHandlers


class CommandHandlersTests(SimpleTestCase):
    def setUp(self) -> None:
        self.handlers = CommandHandlers()

    def test_start_handler_returns_main_menu(self) -> None:
        reply = self.handlers.handle_start(chat_id=123)

        self.assertEqual(reply.chat_id, 123)
        self.assertIn("CarCare botga xush kelibsiz", reply.text)
        self.assertIsNotNone(reply.reply_markup)

    def test_help_handler_returns_help_text(self) -> None:
        reply = self.handlers.handle_help(chat_id=321)

        self.assertEqual(reply.chat_id, 321)
        self.assertIn("/help", reply.text)
        self.assertIsNotNone(reply.reply_markup)
