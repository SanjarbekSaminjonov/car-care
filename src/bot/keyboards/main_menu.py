from typing import Any


def build_main_menu_keyboard() -> dict[str, Any]:
    return {
        "keyboard": [
            [{"text": "🚗 Mening mashinalarim"}, {"text": "➕ Mashina qo'shish"}],
            [{"text": "🛠 Servis qo'shish"}, {"text": "📈 Odometr yangilash"}],
            [{"text": "❓ Yordam"}],
        ],
        "resize_keyboard": True,
    }
