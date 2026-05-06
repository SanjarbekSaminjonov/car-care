from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from bot.clients.telegram import TelegramBotClient
from bot.config.settings import BotSettingsError, get_required_telegram_token
from services.notification_service import (
    enqueue_due_reminder_notifications,
    get_due_notifications,
    send_due_telegram_notifications,
)


class Command(BaseCommand):
    help = "Log due notification and reminder work. Dry-run by default."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--limit", type=int, default=100)
        parser.add_argument(
            "--enqueue-reminders",
            action="store_true",
            help="Create notification events for due reminders instead of only logging them.",
        )
        parser.add_argument(
            "--send-telegram",
            action="store_true",
            help="Send pending Telegram notification events.",
        )

    def handle(self, *args, **options) -> None:
        limit = options["limit"]
        now = timezone.now()

        notifications = get_due_notifications(limit=limit, now=now)
        self.stdout.write(f"Due notifications: {len(notifications)}")
        for notification in notifications:
            self.stdout.write(
                f"- notification={notification.id} type={notification.event_type} "
                f"channel={notification.channel} recipient={notification.recipient or notification.user_id}"
            )

        dry_run = not options["enqueue_reminders"]
        reminder_results = enqueue_due_reminder_notifications(limit=limit, now=now, dry_run=dry_run)
        action = "Due reminders" if dry_run else "Enqueued reminders"
        self.stdout.write(f"{action}: {len(reminder_results)}")
        for result in reminder_results:
            suffix = ""
            if result.notification is not None:
                suffix = f" notification={result.notification.id}"
            self.stdout.write(
                f"- reminder={result.reminder.id} type={result.reminder.reminder_type}{suffix}"
            )

        if options["send_telegram"]:
            try:
                token = get_required_telegram_token()
            except BotSettingsError as exc:
                raise CommandError(str(exc)) from exc

            delivery_results = send_due_telegram_notifications(
                client=TelegramBotClient(token=token),
                limit=limit,
                now=now,
            )
            self.stdout.write(f"Telegram deliveries: {len(delivery_results)}")
            for result in delivery_results:
                status = "sent" if result.delivered else f"failed: {result.error_message}"
                self.stdout.write(f"- notification={result.notification.id} {status}")
