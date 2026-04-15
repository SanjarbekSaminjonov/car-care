from apps.telegram.models import TelegramAccount


def get_telegram_account_for_chat(*, chat_id: int) -> TelegramAccount:
    telegram_account = (
        TelegramAccount.objects.select_related("user")
        .filter(chat_id=chat_id)
        .order_by("-updated_at", "-id")
        .first()
    )
    if telegram_account is None:
        raise TelegramAccount.DoesNotExist(f"No TelegramAccount found for chat_id={chat_id}")

    return telegram_account
