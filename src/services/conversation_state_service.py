from datetime import timedelta
from typing import Any

from django.utils import timezone

from apps.telegram.models import BotConversationState, TelegramAccount


def save_flow_state(
    *,
    chat_id: int,
    flow_name: str,
    state_name: str,
    state_payload: dict[str, Any],
    expires_in_minutes: int = 120,
) -> BotConversationState:
    telegram_account = TelegramAccount.objects.filter(chat_id=chat_id).first()
    expires_at = timezone.now() + timedelta(minutes=expires_in_minutes)

    state, _created = BotConversationState.objects.update_or_create(
        chat_id=chat_id,
        flow_name=flow_name,
        defaults={
            "telegram_account": telegram_account,
            "state_name": state_name,
            "state_payload": state_payload,
            "expires_at": expires_at,
        },
    )
    return state


def get_flow_state(*, chat_id: int, flow_name: str) -> BotConversationState | None:
    state = (
        BotConversationState.objects.filter(
            chat_id=chat_id,
            flow_name=flow_name,
            expires_at__gt=timezone.now(),
        )
        .order_by("-updated_at")
        .first()
    )
    return state


def clear_flow_state(*, chat_id: int, flow_name: str) -> int:
    deleted_count, _ = BotConversationState.objects.filter(
        chat_id=chat_id,
        flow_name=flow_name,
    ).delete()
    return deleted_count


def cleanup_expired_flow_states() -> int:
    deleted_count, _ = BotConversationState.objects.filter(expires_at__lte=timezone.now()).delete()
    return deleted_count
