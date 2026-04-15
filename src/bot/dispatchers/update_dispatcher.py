from typing import Any

from bot.handlers.car_flow import CarFlowHandlers
from bot.handlers.commands import BotReply, CommandHandlers
from bot.handlers.maintenance_flow import MaintenanceFlowHandlers
from bot.handlers.odometer_flow import OdometerFlowHandlers


MAIN_MENU_TEXT_TO_COMMAND = {
    "🚗 Mening mashinalarim": "/cars",
    "➕ Mashina qo'shish": "/addcar",
    "🛠 Servis qo'shish": "/addmaintenance",
    "📈 Odometr yangilash": "/addodometer",
    "❓ Yordam": "/help",
}


class UpdateDispatcher:
    def __init__(self) -> None:
        self.command_handlers = CommandHandlers()
        self.car_flow_handlers = CarFlowHandlers()
        self.maintenance_flow_handlers = MaintenanceFlowHandlers()
        self.odometer_flow_handlers = OdometerFlowHandlers()

    def dispatch(self, update: dict[str, Any]) -> BotReply | None:
        message = update.get("message") or {}
        chat = message.get("chat") or {}
        telegram_user = message.get("from") or {}
        chat_id = chat.get("id")
        telegram_user_id = telegram_user.get("id")
        text = (message.get("text") or "").strip()
        normalized_text = MAIN_MENU_TEXT_TO_COMMAND.get(text, text)

        if not isinstance(chat_id, int):
            return None
        if not isinstance(telegram_user_id, int):
            telegram_user_id = None

        if normalized_text == "/cancel":
            self.car_flow_handlers.cancel(chat_id=chat_id)
            self.maintenance_flow_handlers.cancel(chat_id=chat_id)
            self.odometer_flow_handlers.cancel(chat_id=chat_id)
            return BotReply(chat_id=chat_id, text="Joriy flow bekor qilindi.")

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

        if normalized_text == "/start":
            return self.command_handlers.handle_start(chat_id=chat_id)
        if normalized_text == "/help":
            return self.command_handlers.handle_help(chat_id=chat_id)
        if normalized_text == "/addcar":
            return self.car_flow_handlers.start_add_car(chat_id=chat_id)
        if normalized_text == "/cars":
            return self.car_flow_handlers.list_cars(chat_id=chat_id)
        if normalized_text == "/addmaintenance":
            return self.maintenance_flow_handlers.start_add_maintenance(chat_id=chat_id)
        if normalized_text == "/addodometer":
            return self.odometer_flow_handlers.start_manual_update(chat_id=chat_id)

        return None
