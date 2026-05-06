from datetime import timedelta
from io import StringIO
from unittest import mock

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from apps.cars.models import Car
from apps.notifications.models import NotificationEvent, NotificationStatus, ReminderStatus
from services.notification_service import create_notification_event, create_reminder_event


class ProcessDueNotificationsCommandTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(username="driver", password="secret12345")
        self.car = Car.objects.create(
            plate_number="01C002BC",
            normalized_plate_number="01C002BC",
            brand="Hyundai",
            model="Sonata",
            year=2021,
        )

    def test_dry_run_logs_due_work_without_enqueueing_reminders(self) -> None:
        now = timezone.now()
        create_notification_event(
            user=self.user,
            car=self.car,
            event_type="maintenance.created",
            title="Maintenance saved",
            due_at=now - timedelta(minutes=5),
        )
        reminder = create_reminder_event(
            user=self.user,
            car=self.car,
            title="Oil change",
            due_at=now - timedelta(minutes=5),
        )

        output = StringIO()
        call_command("process_due_notifications", stdout=output)

        self.assertIn("Due notifications: 1", output.getvalue())
        self.assertIn("Due reminders: 1", output.getvalue())
        reminder.refresh_from_db()
        self.assertEqual(reminder.status, ReminderStatus.SCHEDULED)
        self.assertEqual(NotificationEvent.objects.count(), 1)

    def test_enqueue_reminders_creates_notification_event(self) -> None:
        now = timezone.now()
        reminder = create_reminder_event(
            user=self.user,
            car=self.car,
            title="Oil change",
            due_at=now - timedelta(minutes=5),
        )

        output = StringIO()
        call_command("process_due_notifications", "--enqueue-reminders", stdout=output)

        self.assertIn("Enqueued reminders: 1", output.getvalue())
        reminder.refresh_from_db()
        self.assertEqual(reminder.status, ReminderStatus.TRIGGERED)
        self.assertEqual(NotificationEvent.objects.count(), 1)

    def test_send_telegram_option_dispatches_due_notifications(self) -> None:
        now = timezone.now()
        notification = create_notification_event(
            user=self.user,
            car=self.car,
            recipient="123456",
            event_type="reminder.custom",
            title="Check car",
            due_at=now - timedelta(minutes=5),
        )

        output = StringIO()
        with mock.patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "token-123"}, clear=False):
            with mock.patch(
                "apps.notifications.management.commands.process_due_notifications.TelegramBotClient"
            ) as client_class:
                call_command("process_due_notifications", "--send-telegram", stdout=output)

        notification.refresh_from_db()
        self.assertEqual(notification.status, NotificationStatus.SENT)
        client_class.return_value.send_message.assert_called_once_with(
            chat_id=123456,
            text="Check car",
        )
        self.assertIn("Telegram deliveries: 1", output.getvalue())
