from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from apps.cars.models import Car
from apps.notifications.models import NotificationStatus, ReminderStatus, ReminderType
from apps.telegram.models import TelegramAccount
from services.notification_service import (
    create_notification_event,
    create_reminder_event,
    enqueue_due_reminder_notifications,
    get_due_notifications,
    get_due_reminders,
    mark_notification_failed,
    mark_notification_sent,
    send_due_telegram_notifications,
)


class NotificationServiceTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(username="driver", password="secret12345")
        self.car = Car.objects.create(
            plate_number="01B001BC",
            normalized_plate_number="01B001BC",
            brand="Kia",
            model="K5",
            year=2023,
        )

    def test_create_notification_defaults_pending_due_now(self) -> None:
        before = timezone.now()

        notification = create_notification_event(
            user=self.user,
            car=self.car,
            recipient="12345",
            event_type="maintenance.created",
            title="Maintenance saved",
            body="Oil change saved.",
            payload={"record": "abc"},
        )

        self.assertEqual(notification.status, NotificationStatus.PENDING)
        self.assertEqual(notification.attempts, 0)
        self.assertGreaterEqual(notification.due_at, before)
        self.assertEqual(notification.payload, {"record": "abc"})

    def test_dedup_key_returns_existing_notification(self) -> None:
        first = create_notification_event(
            user=self.user,
            car=self.car,
            event_type="reminder.maintenance",
            title="First title",
            dedup_key="reminder:1",
        )

        second = create_notification_event(
            user=self.user,
            car=self.car,
            event_type="reminder.maintenance",
            title="Second title",
            dedup_key="reminder:1",
        )

        self.assertEqual(second.id, first.id)
        self.assertEqual(second.title, "First title")

    def test_get_due_notifications_filters_pending_due_events(self) -> None:
        now = timezone.now()
        due = create_notification_event(
            user=self.user,
            car=self.car,
            event_type="due",
            title="Due",
            due_at=now - timedelta(minutes=1),
        )
        create_notification_event(
            user=self.user,
            car=self.car,
            event_type="future",
            title="Future",
            due_at=now + timedelta(days=1),
        )
        sent = create_notification_event(
            user=self.user,
            car=self.car,
            event_type="sent",
            title="Sent",
            due_at=now - timedelta(minutes=1),
        )
        mark_notification_sent(notification=sent, sent_at=now)

        self.assertEqual(get_due_notifications(now=now), [due])

    def test_mark_notification_sent_and_failed_track_attempts(self) -> None:
        notification = create_notification_event(
            user=self.user,
            car=self.car,
            event_type="test",
            title="Test",
        )

        failed = mark_notification_failed(
            notification=notification,
            failure_reason="transport unavailable",
        )
        self.assertEqual(failed.status, NotificationStatus.FAILED)
        self.assertEqual(failed.attempts, 1)
        self.assertEqual(failed.failure_reason, "transport unavailable")

        sent = mark_notification_sent(notification=failed)
        self.assertEqual(sent.status, NotificationStatus.SENT)
        self.assertEqual(sent.attempts, 2)
        self.assertEqual(sent.failure_reason, "")
        self.assertIsNotNone(sent.sent_at)

    def test_create_reminder_requires_due_condition(self) -> None:
        with self.assertRaises(ValidationError):
            create_reminder_event(car=self.car, user=self.user, title="Oil change")

    def test_due_reminder_dry_run_does_not_write_notification(self) -> None:
        now = timezone.now()
        reminder = create_reminder_event(
            car=self.car,
            user=self.user,
            reminder_type=ReminderType.MAINTENANCE,
            title="Oil change",
            due_at=now - timedelta(hours=1),
        )

        results = enqueue_due_reminder_notifications(now=now, dry_run=True)
        reminder.refresh_from_db()

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].reminder.id, reminder.id)
        self.assertIsNone(results[0].notification)
        self.assertTrue(results[0].dry_run)
        self.assertEqual(reminder.status, ReminderStatus.SCHEDULED)
        self.assertEqual(get_due_reminders(now=now), [reminder])

    def test_enqueue_due_reminder_creates_notification_and_marks_triggered(self) -> None:
        now = timezone.now()
        reminder = create_reminder_event(
            car=self.car,
            user=self.user,
            reminder_type=ReminderType.TIME_BASED,
            title="Check tires",
            body="Tire pressure check is due.",
            due_at=now - timedelta(hours=1),
            payload={"interval_days": 30},
        )

        results = enqueue_due_reminder_notifications(now=now, dry_run=False)
        reminder.refresh_from_db()

        self.assertEqual(len(results), 1)
        self.assertFalse(results[0].dry_run)
        self.assertIsNotNone(results[0].notification)
        self.assertEqual(reminder.status, ReminderStatus.TRIGGERED)
        self.assertEqual(reminder.notification.event_type, "reminder.time_based")
        self.assertEqual(reminder.notification.payload["reminder_id"], str(reminder.id))

    def test_send_due_telegram_notifications_marks_sent(self) -> None:
        TelegramAccount.objects.create(user=self.user, telegram_user_id=101, chat_id=99001)
        notification = create_notification_event(
            user=self.user,
            car=self.car,
            event_type="reminder.time_based",
            title="Check tires",
            body="Tire pressure check is due.",
            due_at=timezone.now() - timedelta(minutes=1),
        )

        class FakeTelegramClient:
            sent_messages: list[dict] = []

            def send_message(self, *, chat_id: int, text: str, reply_markup=None):
                self.sent_messages.append({"chat_id": chat_id, "text": text})
                return {"ok": True}

        client = FakeTelegramClient()

        results = send_due_telegram_notifications(client=client)
        notification.refresh_from_db()

        self.assertEqual(len(results), 1)
        self.assertTrue(results[0].delivered)
        self.assertEqual(notification.status, NotificationStatus.SENT)
        self.assertEqual(notification.attempts, 1)
        self.assertEqual(
            client.sent_messages,
            [{"chat_id": 99001, "text": "Check tires\n\nTire pressure check is due."}],
        )

    def test_send_due_telegram_notifications_marks_failed_without_recipient(self) -> None:
        notification = create_notification_event(
            event_type="reminder.time_based",
            title="Check tires",
            due_at=timezone.now() - timedelta(minutes=1),
        )

        class FakeTelegramClient:
            def send_message(self, *, chat_id: int, text: str, reply_markup=None):
                raise AssertionError("send_message should not be called")

        results = send_due_telegram_notifications(client=FakeTelegramClient())
        notification.refresh_from_db()

        self.assertEqual(len(results), 1)
        self.assertFalse(results[0].delivered)
        self.assertEqual(notification.status, NotificationStatus.FAILED)
        self.assertEqual(notification.attempts, 1)
        self.assertIn("no user", notification.failure_reason)
