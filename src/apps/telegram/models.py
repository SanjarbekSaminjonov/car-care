from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


class TelegramAccount(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="telegram_accounts",
    )
    telegram_user_id = models.BigIntegerField(unique=True)
    chat_id = models.BigIntegerField()
    username = models.CharField(max_length=255, blank=True)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    language_code = models.CharField(max_length=16, blank=True)
    is_blocked = models.BooleanField(default=False)
    last_seen_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "telegram_accounts"
        verbose_name = "telegram account"
        verbose_name_plural = "telegram accounts"
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["chat_id"]),
            models.Index(fields=["is_blocked"]),
        ]

    def __str__(self) -> str:
        username = self.username.strip()
        if username:
            return f"@{username}"
        return str(self.telegram_user_id)


def default_conversation_expiry() -> timezone.datetime:
    return timezone.now() + timedelta(hours=2)


class BotConversationState(models.Model):
    chat_id = models.BigIntegerField()
    telegram_account = models.ForeignKey(
        TelegramAccount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="conversation_states",
    )
    flow_name = models.CharField(max_length=64)
    state_name = models.CharField(max_length=64)
    state_payload = models.JSONField(default=dict, blank=True)
    expires_at = models.DateTimeField(default=default_conversation_expiry)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "bot_conversation_states"
        verbose_name = "bot conversation state"
        verbose_name_plural = "bot conversation states"
        constraints = [
            models.UniqueConstraint(fields=["chat_id", "flow_name"], name="uq_bot_state_chat_flow")
        ]
        indexes = [
            models.Index(fields=["chat_id", "flow_name"]),
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self) -> str:
        return f"chat={self.chat_id} flow={self.flow_name} state={self.state_name}"
