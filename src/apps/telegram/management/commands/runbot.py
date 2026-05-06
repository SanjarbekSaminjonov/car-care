import logging
import time

from django.core.management.base import BaseCommand, CommandError

from bot.clients.telegram import TelegramBotClient
from bot.config.settings import BotSettingsError, get_required_telegram_token
from bot.dispatchers.update_dispatcher import UpdateDispatcher

logger = logging.getLogger(__name__)
ALLOWED_UPDATES = ["message", "callback_query"]


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
                updates = client.get_updates(
                    offset=offset,
                    timeout=poll_timeout,
                    allowed_updates=ALLOWED_UPDATES,
                )
                for update in updates:
                    callback_query_id = self._callback_query_id(update)
                    if callback_query_id is not None:
                        self._answer_callback_query(client, callback_query_id)
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

    def _callback_query_id(self, update: dict) -> str | None:
        callback_query = update.get("callback_query")
        if not isinstance(callback_query, dict):
            return None
        callback_query_id = callback_query.get("id")
        return callback_query_id if isinstance(callback_query_id, str) else None

    def _answer_callback_query(
        self,
        client: TelegramBotClient,
        callback_query_id: str,
    ) -> None:
        try:
            client.answer_callback_query(callback_query_id=callback_query_id)
        except Exception as exc:  # noqa: BLE001
            logger.warning("failed to answer callback query: %s", exc)
