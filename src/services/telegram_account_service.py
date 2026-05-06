from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from apps.telegram.models import TelegramAccount


@transaction.atomic
def sync_telegram_account(
    *,
    chat_id: int,
    telegram_user_id: int,
    username: str = "",
    first_name: str = "",
    last_name: str = "",
    language_code: str = "",
) -> TelegramAccount:
    account = (
        TelegramAccount.objects.select_related("user")
        .filter(telegram_user_id=telegram_user_id)
        .first()
    )
    now = timezone.now()

    if account is None:
        user_model = get_user_model()
        user = user_model.objects.create_user(
            username=f"tg_{telegram_user_id}",
            password=None,
            first_name=first_name.strip(),
            last_name=last_name.strip(),
        )
        return TelegramAccount.objects.create(
            user=user,
            telegram_user_id=telegram_user_id,
            chat_id=chat_id,
            username=username.strip(),
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            language_code=language_code.strip(),
            last_seen_at=now,
        )

    account.chat_id = chat_id
    account.username = username.strip()
    account.first_name = first_name.strip()
    account.last_name = last_name.strip()
    account.language_code = language_code.strip()
    account.last_seen_at = now
    account.save(
        update_fields=[
            "chat_id",
            "username",
            "first_name",
            "last_name",
            "language_code",
            "last_seen_at",
            "updated_at",
        ]
    )
    return account


def get_telegram_account_for_chat(*, chat_id: int, telegram_user_id: int) -> TelegramAccount:
    telegram_account = (
        TelegramAccount.objects.select_related("user")
        .filter(chat_id=chat_id, telegram_user_id=telegram_user_id, is_blocked=False)
        .first()
    )
    if telegram_account is None:
        raise TelegramAccount.DoesNotExist(
            f"No TelegramAccount found for chat_id={chat_id} and telegram_user_id={telegram_user_id}"
        )

    return telegram_account
