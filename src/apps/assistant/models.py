import uuid

from django.conf import settings
from django.db import models

from apps.telegram.models import TelegramAccount


class AssistantInteractionStatus(models.TextChoices):
    SUCCEEDED = "succeeded", "Succeeded"
    FAILED = "failed", "Failed"


class AssistantInteraction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    telegram_account = models.ForeignKey(
        TelegramAccount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assistant_interactions",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assistant_interactions",
    )
    chat_id = models.BigIntegerField()
    question = models.TextField()
    answer = models.TextField(blank=True)
    provider = models.CharField(max_length=64)
    model_name = models.CharField(max_length=128)
    status = models.CharField(
        max_length=16,
        choices=AssistantInteractionStatus.choices,
        default=AssistantInteractionStatus.SUCCEEDED,
    )
    car_context = models.JSONField(default=dict, blank=True)
    response_metadata = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "assistant_interactions"
        verbose_name = "assistant interaction"
        verbose_name_plural = "assistant interactions"
        indexes = [
            models.Index(fields=["chat_id", "created_at"], name="assistant_chat_created_idx"),
            models.Index(fields=["user", "created_at"], name="assistant_user_created_idx"),
            models.Index(fields=["status"], name="assistant_status_idx"),
        ]

    def __str__(self) -> str:
        if self.created_at is None:
            return f"{self.chat_id} {self.status}"
        return f"{self.chat_id} {self.status} {self.created_at:%Y-%m-%d %H:%M:%S}"
