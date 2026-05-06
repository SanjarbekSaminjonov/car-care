import hashlib
import hmac
import json
from dataclasses import dataclass
from time import time
from urllib.parse import parse_qsl

from django.conf import settings
from django.core.exceptions import ValidationError


@dataclass(frozen=True)
class TelegramWebAppUser:
    telegram_user_id: int
    username: str = ""
    first_name: str = ""
    last_name: str = ""
    language_code: str = ""


@dataclass(frozen=True)
class TelegramInitData:
    user: TelegramWebAppUser
    auth_date: int
    chat_id: int


def validate_telegram_init_data(init_data: str) -> TelegramInitData:
    parsed = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = parsed.pop("hash", "")
    if not received_hash:
        raise ValidationError("Telegram initData hash topilmadi.")

    bot_token = settings.TELEGRAM_BOT_TOKEN
    if not bot_token:
        raise ValidationError("Telegram bot token sozlanmagan.")

    data_check_string = "\n".join(
        f"{key}={value}" for key, value in sorted(parsed.items())
    )
    secret_key = hmac.new(
        b"WebAppData",
        bot_token.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(calculated_hash, received_hash):
        raise ValidationError("Telegram initData imzosi noto'g'ri.")

    auth_date = _parse_auth_date(parsed.get("auth_date", ""))
    max_age_seconds = settings.TELEGRAM_WEBAPP_AUTH_MAX_AGE_SECONDS
    if max_age_seconds > 0 and time() - auth_date > max_age_seconds:
        raise ValidationError("Telegram sessiyasi eskirgan. Appni qayta oching.")

    user = _parse_user(parsed.get("user", ""))
    chat_id = _parse_chat_id(parsed.get("chat", ""), default=user.telegram_user_id)
    return TelegramInitData(user=user, auth_date=auth_date, chat_id=chat_id)


def _parse_auth_date(raw_auth_date: str) -> int:
    try:
        auth_date = int(raw_auth_date)
    except (TypeError, ValueError) as exc:
        raise ValidationError("Telegram auth_date noto'g'ri.") from exc
    if auth_date <= 0:
        raise ValidationError("Telegram auth_date noto'g'ri.")
    return auth_date


def _parse_user(raw_user: str) -> TelegramWebAppUser:
    try:
        payload = json.loads(raw_user)
    except json.JSONDecodeError as exc:
        raise ValidationError("Telegram user ma'lumoti noto'g'ri.") from exc

    telegram_user_id = payload.get("id")
    if not isinstance(telegram_user_id, int):
        raise ValidationError("Telegram user id topilmadi.")

    return TelegramWebAppUser(
        telegram_user_id=telegram_user_id,
        username=str(payload.get("username") or ""),
        first_name=str(payload.get("first_name") or ""),
        last_name=str(payload.get("last_name") or ""),
        language_code=str(payload.get("language_code") or ""),
    )


def _parse_chat_id(raw_chat: str, *, default: int) -> int:
    if not raw_chat:
        return default
    try:
        payload = json.loads(raw_chat)
    except json.JSONDecodeError:
        return default
    chat_id = payload.get("id")
    return chat_id if isinstance(chat_id, int) else default
