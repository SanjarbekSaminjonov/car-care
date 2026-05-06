from typing import Any

from django.conf import settings


def build_webapp_button() -> dict[str, Any] | None:
    if not settings.TELEGRAM_WEBAPP_URL:
        return None
    return {"text": "🌐 CarCare App", "web_app": {"url": settings.TELEGRAM_WEBAPP_URL}}


def build_webapp_inline_keyboard() -> dict[str, Any] | None:
    if not settings.TELEGRAM_WEBAPP_URL:
        return None
    return {
        "inline_keyboard": [
            [{"text": "🌐 CarCare App", "web_app": {"url": settings.TELEGRAM_WEBAPP_URL}}]
        ]
    }


def build_main_menu_keyboard() -> dict[str, Any]:
    keyboard = [
        [{"text": "🚗 Mening mashinalarim"}, {"text": "➕ Mashina qo'shish"}],
        [{"text": "🛠 Servis qo'shish"}, {"text": "📈 Odometr yangilash"}],
        [{"text": "📋 Servis tarixi"}, {"text": "🔗 Mashina ulashish"}],
        [{"text": "❓ Yordam"}],
    ]
    webapp_button = build_webapp_button()
    if webapp_button is not None:
        keyboard.insert(0, [webapp_button])
    return {
        "keyboard": keyboard,
        "resize_keyboard": True,
    }
