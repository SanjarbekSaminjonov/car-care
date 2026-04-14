import logging
import time

from django.core.management.base import BaseCommand, CommandError

from bot.clients.telegram import TelegramBotClient
from bot.config.settings import BotSettingsError, get_required_telegram_token
from bot.dispatchers.update_dispatcher import UpdateDispatcher

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Run Telegram bot polling loop."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--poll-timeout", type=int, default=25)
        parser.add_argument("--sleep-seconds", type=float, default=1.0)

    def handle(self, *args, **options):
        try:
            token = get_required_telegram_token()
        except BotSettingsError as exc:
            raise CommandError(str(exc)) from exc

        poll_timeout: int = options["poll_timeout"]
        sleep_seconds: float = options["sleep_seconds"]

        client = TelegramBotClient(token=token)
        dispatcher = UpdateDispatcher()
        offset: int | None = None

        logger.info("runbot started")
        self.stdout.write(self.style.SUCCESS("runbot started"))

        try:
            while True:
                updates = client.get_updates(offset=offset, timeout=poll_timeout)
                for update in updates:
                    reply = dispatcher.dispatch(update)
                    if reply is not None:
                        client.send_message(
                            chat_id=reply.chat_id,
                            text=reply.text,
                            reply_markup=reply.reply_markup,
                        )
                    update_id = update.get("update_id")
                    if isinstance(update_id, int):
                        offset = update_id + 1
                time.sleep(sleep_seconds)
        except KeyboardInterrupt:
            logger.info("runbot stopped")
            self.stdout.write(self.style.WARNING("runbot stopped"))
        except Exception as exc:  # noqa: BLE001
            logger.exception("runbot error: %s", exc)
            raise CommandError("runbot terminated with an unexpected error") from exc
