from django.test import SimpleTestCase, override_settings

from bot.keyboards.main_menu import build_main_menu_keyboard


class MainMenuKeyboardTests(SimpleTestCase):
    @override_settings(TELEGRAM_WEBAPP_URL="https://example.com/app/")
    def test_webapp_button_is_first_when_configured(self) -> None:
        keyboard = build_main_menu_keyboard()

        self.assertEqual(
            keyboard["keyboard"][0],
            [{"text": "🌐 CarCare App", "web_app": {"url": "https://example.com/app/"}}],
        )
