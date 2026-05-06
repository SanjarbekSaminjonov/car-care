from dataclasses import dataclass
from typing import Any

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.notifications.models import (
    NotificationChannel,
    NotificationEvent,
    NotificationStatus,
    ReminderEvent,
    ReminderStatus,
    ReminderType,
)
from apps.telegram.models import TelegramAccount


@dataclass(frozen=True)
class ReminderNotificationResult:
    reminder: ReminderEvent
    notification: NotificationEvent | None
    dry_run: bool


@dataclass(frozen=True)
class NotificationDeliveryResult:
    notification: NotificationEvent
    delivered: bool
    error_message: str = ""


def _validate_text(value: str, message: str) -> str:
    value = value.strip()
    if not value:
        raise ValidationError(message)
    return value


@transaction.atomic
def create_notification_event(
    *,
    event_type: str,
    title: str,
    user=None,
    car=None,
    channel: str = NotificationChannel.TELEGRAM,
    recipient: str = "",
    body: str = "",
    payload: dict[str, Any] | None = None,
    due_at=None,
    dedup_key: str | None = None,
) -> NotificationEvent:
    event_type = _validate_text(event_type, "Notification event type is required.")
    title = _validate_text(title, "Notification title is required.")
    due_at = due_at or timezone.now()

    create_kwargs = {
        "user": user,
        "car": car,
        "channel": channel,
        "recipient": recipient.strip(),
        "event_type": event_type,
        "title": title,
        "body": body.strip(),
        "payload": payload or {},
        "due_at": due_at,
    }

    if dedup_key:
        notification, _ = NotificationEvent.objects.get_or_create(
            dedup_key=dedup_key.strip(),
            defaults=create_kwargs,
        )
        return notification

    return NotificationEvent.objects.create(**create_kwargs)


def get_due_notifications(*, limit: int = 100, now=None) -> list[NotificationEvent]:
    if limit <= 0:
        raise ValidationError("Limit must be positive.")

    due_at = now or timezone.now()
    return list(
        NotificationEvent.objects.select_related("user", "car")
        .filter(status=NotificationStatus.PENDING, due_at__lte=due_at)
        .order_by("due_at", "created_at")[:limit]
    )


def get_due_telegram_notifications(*, limit: int = 100, now=None) -> list[NotificationEvent]:
    if limit <= 0:
        raise ValidationError("Limit must be positive.")

    due_at = now or timezone.now()
    return list(
        NotificationEvent.objects.select_related("user", "car")
        .filter(
            status=NotificationStatus.PENDING,
            due_at__lte=due_at,
            channel=NotificationChannel.TELEGRAM,
        )
        .order_by("due_at", "created_at")[:limit]
    )


@transaction.atomic
def mark_notification_sent(*, notification: NotificationEvent, sent_at=None) -> NotificationEvent:
    locked = NotificationEvent.objects.select_for_update().get(pk=notification.pk)
    now = sent_at or timezone.now()
    locked.status = NotificationStatus.SENT
    locked.sent_at = now
    locked.last_attempt_at = now
    locked.attempts += 1
    locked.failure_reason = ""
    locked.save(
        update_fields=[
            "status",
            "sent_at",
            "last_attempt_at",
            "attempts",
            "failure_reason",
            "updated_at",
        ]
    )
    return locked


@transaction.atomic
def mark_notification_failed(
    *, notification: NotificationEvent, failure_reason: str, failed_at=None
) -> NotificationEvent:
    locked = NotificationEvent.objects.select_for_update().get(pk=notification.pk)
    now = failed_at or timezone.now()
    locked.status = NotificationStatus.FAILED
    locked.last_attempt_at = now
    locked.attempts += 1
    locked.failure_reason = failure_reason.strip()
    locked.save(
        update_fields=[
            "status",
            "last_attempt_at",
            "attempts",
            "failure_reason",
            "updated_at",
        ]
    )
    return locked


def _resolve_telegram_chat_id(notification: NotificationEvent) -> int:
    recipient = notification.recipient.strip()
    if recipient:
        try:
            return int(recipient)
        except ValueError as exc:
            raise ValidationError("Telegram recipient must be a numeric chat_id.") from exc

    if notification.user_id is None:
        raise ValidationError("Notification has no user or Telegram recipient.")

    account = (
        TelegramAccount.objects.filter(user_id=notification.user_id, is_blocked=False)
        .order_by("-last_seen_at", "-updated_at")
        .first()
    )
    if account is None:
        raise ValidationError("User has no active Telegram account.")

    return account.chat_id


def _render_notification_text(notification: NotificationEvent) -> str:
    body = notification.body.strip()
    if body:
        return f"{notification.title}\n\n{body}"
    return notification.title


def send_due_telegram_notifications(
    *,
    client,
    limit: int = 100,
    now=None,
) -> list[NotificationDeliveryResult]:
    results: list[NotificationDeliveryResult] = []
    for notification in get_due_telegram_notifications(limit=limit, now=now):
        try:
            chat_id = _resolve_telegram_chat_id(notification)
            client.send_message(chat_id=chat_id, text=_render_notification_text(notification))
        except Exception as exc:  # noqa: BLE001
            failed = mark_notification_failed(
                notification=notification,
                failure_reason=str(exc)[:2000],
            )
            results.append(
                NotificationDeliveryResult(
                    notification=failed,
                    delivered=False,
                    error_message=failed.failure_reason,
                )
            )
            continue

        sent = mark_notification_sent(notification=notification)
        results.append(NotificationDeliveryResult(notification=sent, delivered=True))

    return results


def create_reminder_event(
    *,
    car,
    title: str,
    user=None,
    reminder_type: str = ReminderType.CUSTOM,
    body: str = "",
    payload: dict[str, Any] | None = None,
    due_at=None,
    odometer_due: int | None = None,
    source_object_type: str = "",
    source_object_id: str = "",
) -> ReminderEvent:
    title = _validate_text(title, "Reminder title is required.")
    if due_at is None and odometer_due is None:
        raise ValidationError("Reminder requires due_at or odometer_due.")
    if odometer_due is not None and odometer_due <= 0:
        raise ValidationError("Reminder odometer_due must be positive.")

    return ReminderEvent.objects.create(
        user=user,
        car=car,
        reminder_type=reminder_type,
        title=title,
        body=body.strip(),
        payload=payload or {},
        due_at=due_at,
        odometer_due=odometer_due,
        source_object_type=source_object_type.strip(),
        source_object_id=str(source_object_id).strip(),
    )


def get_due_reminders(*, limit: int = 100, now=None) -> list[ReminderEvent]:
    if limit <= 0:
        raise ValidationError("Limit must be positive.")

    due_at = now or timezone.now()
    return list(
        ReminderEvent.objects.select_related("user", "car")
        .filter(status=ReminderStatus.SCHEDULED, due_at__isnull=False, due_at__lte=due_at)
        .order_by("due_at", "created_at")[:limit]
    )


@transaction.atomic
def enqueue_due_reminder_notifications(
    *, limit: int = 100, now=None, dry_run: bool = True
) -> list[ReminderNotificationResult]:
    due_at = now or timezone.now()
    reminders = get_due_reminders(limit=limit, now=due_at)
    results: list[ReminderNotificationResult] = []

    if dry_run:
        return [
            ReminderNotificationResult(reminder=reminder, notification=None, dry_run=True)
            for reminder in reminders
        ]

    for reminder in reminders:
        locked = ReminderEvent.objects.select_for_update().get(pk=reminder.pk)
        if locked.status != ReminderStatus.SCHEDULED:
            continue

        notification = create_notification_event(
            user=locked.user,
            car=locked.car,
            event_type=f"reminder.{locked.reminder_type}",
            title=locked.title,
            body=locked.body,
            payload={
                **locked.payload,
                "reminder_id": str(locked.id),
                "reminder_type": locked.reminder_type,
            },
            due_at=due_at,
            dedup_key=f"reminder:{locked.id}",
        )
        locked.notification = notification
        locked.status = ReminderStatus.TRIGGERED
        locked.triggered_at = due_at
        locked.save(update_fields=["notification", "status", "triggered_at", "updated_at"])
        results.append(
            ReminderNotificationResult(reminder=locked, notification=notification, dry_run=False)
        )

    return results
