from apps.cars.models import Car
from apps.telegram.models import TelegramAccount


def list_cars_for_chat(*, chat_id: int) -> list[Car]:
    telegram_account = (
        TelegramAccount.objects.only("user_id").filter(chat_id=chat_id).first()
    )
    if telegram_account is None:
        return []

    return list(
        Car.objects.filter(memberships__user_id=telegram_account.user_id)
        .distinct()
        .order_by("-created_at")
    )
