import os


class BotSettingsError(RuntimeError):
    """Raised when required bot settings are missing."""


def get_required_telegram_token() -> str:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        raise BotSettingsError(
            "TELEGRAM_BOT_TOKEN is required to run the bot. Set it in environment."
        )
    return token
