import uuid

from django.conf import settings
from django.db import models


class NotificationChannel(models.TextChoices):
    TELEGRAM = "telegram", "Telegram"
    EMAIL = "email", "Email"
    IN_APP = "in_app", "In app"
    SYSTEM = "system", "System"


class NotificationStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    SENT = "sent", "Sent"
    FAILED = "failed", "Failed"
    CANCELLED = "cancelled", "Cancelled"


class ReminderType(models.TextChoices):
    TIME_BASED = "time_based", "Time based"
    ODOMETER = "odometer", "Odometer"
    MAINTENANCE = "maintenance", "Maintenance"
    CUSTOM = "custom", "Custom"


class ReminderStatus(models.TextChoices):
    SCHEDULED = "scheduled", "Scheduled"
    TRIGGERED = "triggered", "Triggered"
    CANCELLED = "cancelled", "Cancelled"


class NotificationEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notification_events",
    )
    car = models.ForeignKey(
        "cars.Car",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notification_events",
    )
    channel = models.CharField(
        max_length=32,
        choices=NotificationChannel.choices,
        default=NotificationChannel.TELEGRAM,
    )
    recipient = models.CharField(max_length=255, blank=True)
    event_type = models.CharField(max_length=128)
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    payload = models.JSONField(default=dict, blank=True)
    due_at = models.DateTimeField()
    status = models.CharField(
        max_length=32,
        choices=NotificationStatus.choices,
        default=NotificationStatus.PENDING,
    )
    attempts = models.PositiveSmallIntegerField(default=0)
    dedup_key = models.CharField(max_length=255, unique=True, null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    last_attempt_at = models.DateTimeField(null=True, blank=True)
    failure_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "notification_events"
        verbose_name = "notification event"
        verbose_name_plural = "notification events"
        indexes = [
            models.Index(fields=["status", "due_at"], name="notif_status_due_idx"),
            models.Index(fields=["user", "status"], name="notif_user_status_idx"),
            models.Index(fields=["car", "due_at"], name="notif_car_due_idx"),
            models.Index(fields=["event_type"], name="notif_event_type_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.event_type} -> {self.recipient or self.user_id}"


class ReminderEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reminder_events",
    )
    car = models.ForeignKey(
        "cars.Car",
        on_delete=models.CASCADE,
        related_name="reminder_events",
    )
    reminder_type = models.CharField(
        max_length=32,
        choices=ReminderType.choices,
        default=ReminderType.CUSTOM,
    )
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    payload = models.JSONField(default=dict, blank=True)
    due_at = models.DateTimeField(null=True, blank=True)
    odometer_due = models.PositiveBigIntegerField(null=True, blank=True)
    source_object_type = models.CharField(max_length=128, blank=True)
    source_object_id = models.CharField(max_length=128, blank=True)
    status = models.CharField(
        max_length=32,
        choices=ReminderStatus.choices,
        default=ReminderStatus.SCHEDULED,
    )
    notification = models.ForeignKey(
        NotificationEvent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reminder_events",
    )
    triggered_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "reminder_events"
        verbose_name = "reminder event"
        verbose_name_plural = "reminder events"
        indexes = [
            models.Index(fields=["status", "due_at"], name="remind_status_due_idx"),
            models.Index(fields=["car", "status"], name="remind_car_status_idx"),
            models.Index(fields=["user", "status"], name="remind_user_status_idx"),
            models.Index(fields=["source_object_type", "source_object_id"], name="remind_source_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.status})"
