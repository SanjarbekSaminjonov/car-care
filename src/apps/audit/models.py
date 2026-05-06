import uuid

from django.conf import settings
from django.db import models


class AuditActorType(models.TextChoices):
    USER = "user", "User"
    SYSTEM = "system", "System"
    WORKER = "worker", "Worker"
    TELEGRAM = "telegram", "Telegram"
    ADMIN = "admin", "Admin"


class AuditEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_events",
    )
    actor_type = models.CharField(
        max_length=32,
        choices=AuditActorType.choices,
        default=AuditActorType.USER,
    )
    action = models.CharField(max_length=128)
    entity_type = models.CharField(max_length=128)
    entity_id = models.CharField(max_length=128, blank=True)
    car = models.ForeignKey(
        "cars.Car",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_events",
    )
    context = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    occurred_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "audit_events"
        verbose_name = "audit event"
        verbose_name_plural = "audit events"
        indexes = [
            models.Index(fields=["actor", "occurred_at"], name="audit_actor_time_idx"),
            models.Index(fields=["action", "occurred_at"], name="audit_action_time_idx"),
            models.Index(fields=["entity_type", "entity_id"], name="audit_entity_idx"),
            models.Index(fields=["car", "occurred_at"], name="audit_car_time_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.action} {self.entity_type}:{self.entity_id}"
