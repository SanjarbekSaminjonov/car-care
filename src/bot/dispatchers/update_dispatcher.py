from typing import Any

from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.telegram.models import ProcessedTelegramUpdate
from bot.handlers.ai_assistant import AIAssistantHandlers
from bot.handlers.car_flow import CarFlowHandlers
from bot.handlers.commands import BotReply, CommandHandlers
from bot.handlers.maintenance_flow import MaintenanceFlowHandlers
from bot.handlers.odometer_flow import OdometerFlowHandlers
from bot.handlers.share_flow import ShareFlowHandlers
from services.telegram_account_service import sync_telegram_account


MAIN_MENU_TEXT_TO_COMMAND = {
    "🚗 Mening mashinalarim": "/cars",
    "➕ Mashina qo'shish": "/addcar",
    "🛠 Servis qo'shish": "/addmaintenance",
    "📈 Odometr yangilash": "/addodometer",
    "📋 Servis tarixi": "/history",
    "🔗 Mashina ulashish": "/share",
    "❓ Yordam": "/help",
}


class UpdateDispatcher:
    def __init__(self) -> None:
        self.command_handlers = CommandHandlers()
        self.car_flow_handlers = CarFlowHandlers()
        self.maintenance_flow_handlers = MaintenanceFlowHandlers()
        self.odometer_flow_handlers = OdometerFlowHandlers()
        self.ai_assistant_handlers = AIAssistantHandlers()
        self.share_flow_handlers = ShareFlowHandlers()

    def dispatch(self, update: dict[str, Any]) -> BotReply | None:
        update_id = update.get("update_id")
        if not isinstance(update_id, int):
            return self._dispatch_update(update)

        update_claim = self._claim_update(update_id=update_id, update=update)
        if update_claim is None:
            return None

        try:
            reply = self._dispatch_update(update)
        except Exception:
            update_claim.delete()
            raise

        ProcessedTelegramUpdate.objects.filter(pk=update_claim.pk).update(
            status=ProcessedTelegramUpdate.Status.PROCESSED,
            processed_at=timezone.now(),
        )
        return reply

    def _claim_update(
        self,
        *,
        update_id: int,
        update: dict[str, Any],
    ) -> ProcessedTelegramUpdate | None:
        try:
            with transaction.atomic():
                return ProcessedTelegramUpdate.objects.create(
                    update_id=update_id,
                    status=ProcessedTelegramUpdate.Status.PROCESSING,
                    processed_at=None,
                    **self._processed_update_metadata(update),
                )
        except IntegrityError:
            if ProcessedTelegramUpdate.objects.filter(update_id=update_id).exists():
                return None
            raise

    def _dispatch_update(self, update: dict[str, Any]) -> BotReply | None:
        message, telegram_user, text = self._dispatch_payload(update)
        chat = message.get("chat") or {}
        chat_id = chat.get("id")
        telegram_user_id = telegram_user.get("id")
        normalized_text = MAIN_MENU_TEXT_TO_COMMAND.get(text, text)

        if not isinstance(chat_id, int):
            return None
        if not isinstance(telegram_user_id, int):
            telegram_user_id = None
        else:
            sync_telegram_account(
                chat_id=chat_id,
                telegram_user_id=telegram_user_id,
                username=str(telegram_user.get("username") or ""),
                first_name=str(telegram_user.get("first_name") or ""),
                last_name=str(telegram_user.get("last_name") or ""),
                language_code=str(telegram_user.get("language_code") or ""),
            )

        if normalized_text == "/cancel":
            self._clear_interactive_flows(chat_id=chat_id)
            return BotReply(chat_id=chat_id, text="Joriy flow bekor qilindi.")

        if any(media_key in message for media_key in ("photo", "document", "video", "audio")):
            media_reply = self.maintenance_flow_handlers.handle_media_input(
                chat_id=chat_id,
                message=message,
                telegram_user_id=telegram_user_id,
            )
            if media_reply is not None:
                return media_reply

        command_reply = self._dispatch_command(
            chat_id=chat_id,
            telegram_user_id=telegram_user_id,
            normalized_text=normalized_text,
        )
        if command_reply is not None:
            return command_reply

        share_reply = self.share_flow_handlers.handle_flow_input(
            chat_id=chat_id,
            text=normalized_text,
            telegram_user_id=telegram_user_id,
        )
        if share_reply is not None:
            return share_reply

        ai_reply = self.ai_assistant_handlers.handle_flow_input(
            chat_id=chat_id,
            text=normalized_text,
            telegram_user_id=telegram_user_id,
        )
        if ai_reply is not None:
            return ai_reply

        maintenance_reply = self.maintenance_flow_handlers.handle_flow_input(
            chat_id=chat_id,
            text=normalized_text,
            telegram_user_id=telegram_user_id,
        )
        if maintenance_reply is not None:
            return maintenance_reply

        odometer_reply = self.odometer_flow_handlers.handle_flow_input(
            chat_id=chat_id,
            text=normalized_text,
            telegram_user_id=telegram_user_id,
        )
        if odometer_reply is not None:
            return odometer_reply

        car_reply = self.car_flow_handlers.handle_flow_input(
            chat_id=chat_id,
            text=normalized_text,
            telegram_user_id=telegram_user_id,
        )
        if car_reply is not None:
            return car_reply

        return None

    def _clear_interactive_flows(self, *, chat_id: int) -> None:
        self.car_flow_handlers.cancel(chat_id=chat_id)
        self.maintenance_flow_handlers.cancel(chat_id=chat_id)
        self.odometer_flow_handlers.cancel(chat_id=chat_id)
        self.ai_assistant_handlers.cancel(chat_id=chat_id)
        self.share_flow_handlers.cancel(chat_id=chat_id)

    def _dispatch_command(
        self,
        *,
        chat_id: int,
        telegram_user_id: int | None,
        normalized_text: str,
    ) -> BotReply | None:
        if not normalized_text.startswith("/"):
            return None

        if normalized_text == "/start":
            self._clear_interactive_flows(chat_id=chat_id)
            return self.command_handlers.handle_start(chat_id=chat_id)
        if normalized_text == "/help":
            self._clear_interactive_flows(chat_id=chat_id)
            return self.command_handlers.handle_help(chat_id=chat_id)
        if normalized_text == "/app":
            self._clear_interactive_flows(chat_id=chat_id)
            return self.command_handlers.handle_app(chat_id=chat_id)
        if normalized_text == "/addcar":
            self._clear_interactive_flows(chat_id=chat_id)
            return self.car_flow_handlers.start_add_car(chat_id=chat_id)
        if normalized_text == "/cars":
            self._clear_interactive_flows(chat_id=chat_id)
            return self.car_flow_handlers.list_cars(chat_id=chat_id)
        if normalized_text == "/addmaintenance":
            self._clear_interactive_flows(chat_id=chat_id)
            return self.maintenance_flow_handlers.start_add_maintenance(chat_id=chat_id)
        if normalized_text == "/addodometer":
            self._clear_interactive_flows(chat_id=chat_id)
            return self.odometer_flow_handlers.start_manual_update(chat_id=chat_id)
        if normalized_text == "/history" or normalized_text.startswith("/history "):
            self._clear_interactive_flows(chat_id=chat_id)
            return self.maintenance_flow_handlers.show_history(
                chat_id=chat_id,
                plate_number=normalized_text.removeprefix("/history").strip(),
            )
        if normalized_text == "/attachmedia" or normalized_text.startswith("/attachmedia "):
            self._clear_interactive_flows(chat_id=chat_id)
            return self.maintenance_flow_handlers.start_attach_media(
                chat_id=chat_id,
                plate_number=normalized_text.removeprefix("/attachmedia").strip(),
            )
        if normalized_text == "/share" or normalized_text.startswith("/share "):
            self._clear_interactive_flows(chat_id=chat_id)
            return self.share_flow_handlers.start_share(
                chat_id=chat_id,
                telegram_user_id=telegram_user_id,
                args=normalized_text.removeprefix("/share").strip(),
            )
        if normalized_text == "/join" or normalized_text.startswith("/join "):
            self._clear_interactive_flows(chat_id=chat_id)
            return self.share_flow_handlers.accept_invite(
                chat_id=chat_id,
                telegram_user_id=telegram_user_id,
                token=normalized_text.removeprefix("/join").strip(),
            )
        if normalized_text == "/ask" or normalized_text.startswith("/ask "):
            self._clear_interactive_flows(chat_id=chat_id)
            return self.ai_assistant_handlers.start_ask(
                chat_id=chat_id,
                telegram_user_id=telegram_user_id,
                question=normalized_text.removeprefix("/ask").strip(),
            )
        if normalized_text == "/ai" or normalized_text.startswith("/ai "):
            self._clear_interactive_flows(chat_id=chat_id)
            return self.ai_assistant_handlers.start_ask(
                chat_id=chat_id,
                telegram_user_id=telegram_user_id,
                question=normalized_text.removeprefix("/ai").strip(),
            )

        return None

    def _processed_update_metadata(self, update: dict[str, Any]) -> dict[str, Any]:
        update_type, payload = self._first_update_payload(update)
        chat = payload.get("chat") or {}
        telegram_user = payload.get("from") or {}
        callback_query = update.get("callback_query")
        if isinstance(callback_query, dict):
            callback_user = callback_query.get("from") or {}
            if isinstance(callback_user, dict):
                telegram_user = callback_user
        chat_id = chat.get("id")
        telegram_user_id = telegram_user.get("id")

        return {
            "chat_id": chat_id if isinstance(chat_id, int) else None,
            "telegram_user_id": telegram_user_id if isinstance(telegram_user_id, int) else None,
            "update_type": update_type,
        }

    def _dispatch_payload(self, update: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], str]:
        callback_query = update.get("callback_query")
        if isinstance(callback_query, dict):
            message = callback_query.get("message") or {}
            telegram_user = callback_query.get("from") or {}
            data = callback_query.get("data")
            return (
                message if isinstance(message, dict) else {},
                telegram_user if isinstance(telegram_user, dict) else {},
                str(data or "").strip(),
            )

        message = update.get("message") or {}
        if not isinstance(message, dict):
            return {}, {}, ""
        telegram_user = message.get("from") or {}
        return (
            message,
            telegram_user if isinstance(telegram_user, dict) else {},
            str(message.get("text") or "").strip(),
        )

    def _first_update_payload(self, update: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        for update_type in (
            "message",
            "edited_message",
            "callback_query",
            "channel_post",
            "edited_channel_post",
        ):
            payload = update.get(update_type)
            if isinstance(payload, dict):
                if update_type == "callback_query":
                    message = payload.get("message")
                    if isinstance(message, dict):
                        return update_type, message
                return update_type, payload
        return "", {}
