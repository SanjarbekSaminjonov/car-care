import hashlib
import hmac
import json
from time import time
from urllib.parse import urlencode

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase, override_settings

from apps.webapp.auth import validate_telegram_init_data


def signed_init_data(*, bot_token: str = "token-123", user_id: int = 1001) -> str:
    payload = {
        "auth_date": str(int(time())),
        "query_id": "query-1",
        "user": json.dumps(
            {
                "id": user_id,
                "first_name": "Driver",
                "username": "driver",
                "language_code": "uz",
            },
            separators=(",", ":"),
        ),
    }
    data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(payload.items()))
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    payload["hash"] = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    return urlencode(payload)


class TelegramWebAppAuthTests(SimpleTestCase):
    @override_settings(TELEGRAM_BOT_TOKEN="token-123", TELEGRAM_WEBAPP_AUTH_MAX_AGE_SECONDS=86400)
    def test_validates_signed_init_data(self) -> None:
        parsed = validate_telegram_init_data(signed_init_data())

        self.assertEqual(parsed.user.telegram_user_id, 1001)
        self.assertEqual(parsed.user.username, "driver")
        self.assertEqual(parsed.chat_id, 1001)

    @override_settings(TELEGRAM_BOT_TOKEN="token-123", TELEGRAM_WEBAPP_AUTH_MAX_AGE_SECONDS=86400)
    def test_rejects_invalid_hash(self) -> None:
        with self.assertRaises(ValidationError):
            validate_telegram_init_data(f"{signed_init_data()}tampered=1")
