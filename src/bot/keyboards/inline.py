from typing import Any

ODOMETER_CONFIRM_CALLBACK = "odometer:confirm"
ODOMETER_CANCEL_CALLBACK = "odometer:cancel"
MAINTENANCE_DATE_TODAY_CALLBACK = "maintenance:date:today"
MAINTENANCE_CONFIRM_CALLBACK = "maintenance:confirm"
MAINTENANCE_CANCEL_CALLBACK = "maintenance:cancel"


def build_today_date_keyboard() -> dict[str, Any]:
    return {
        "inline_keyboard": [
            [{"text": "Bugun", "callback_data": MAINTENANCE_DATE_TODAY_CALLBACK}]
        ]
    }


def build_confirmation_keyboard(
    *,
    confirm_callback: str,
    cancel_callback: str,
) -> dict[str, Any]:
    return {
        "inline_keyboard": [
            [
                {"text": "✅ Tasdiqlash", "callback_data": confirm_callback},
                {"text": "Bekor qilish", "callback_data": cancel_callback},
            ]
        ]
    }
