from django.test import SimpleTestCase, override_settings

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

    @override_settings(TELEGRAM_WEBAPP_URL="https://example.com/app/")
    def test_app_handler_returns_webapp_button(self) -> None:
        reply = self.handlers.handle_app(chat_id=321)

        self.assertEqual(reply.chat_id, 321)
        self.assertIn("Web App", reply.text)
        self.assertEqual(
            reply.reply_markup,
            {
                "inline_keyboard": [
                    [{"text": "🌐 CarCare App", "web_app": {"url": "https://example.com/app/"}}]
                ]
            },
        )
