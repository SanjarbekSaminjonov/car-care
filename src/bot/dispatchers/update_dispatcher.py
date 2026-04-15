from typing import Any

from bot.handlers.car_flow import CarFlowHandlers
from bot.handlers.commands import BotReply, CommandHandlers
from bot.handlers.maintenance_flow import MaintenanceFlowHandlers
from bot.handlers.odometer_flow import OdometerFlowHandlers


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

        if not isinstance(chat_id, int):
            return None
        if not isinstance(telegram_user_id, int):
            telegram_user_id = None

        if text == "/cancel":
            self.car_flow_handlers.cancel(chat_id=chat_id)
            self.maintenance_flow_handlers.cancel(chat_id=chat_id)
            self.odometer_flow_handlers.cancel(chat_id=chat_id)
            return BotReply(chat_id=chat_id, text="Joriy flow bekor qilindi.")

        maintenance_reply = self.maintenance_flow_handlers.handle_flow_input(
            chat_id=chat_id,
            text=text,
            telegram_user_id=telegram_user_id,
        )
        if maintenance_reply is not None:
            return maintenance_reply

        odometer_reply = self.odometer_flow_handlers.handle_flow_input(
            chat_id=chat_id,
            text=text,
            telegram_user_id=telegram_user_id,
        )
        if odometer_reply is not None:
            return odometer_reply

        car_reply = self.car_flow_handlers.handle_flow_input(
            chat_id=chat_id,
            text=text,
            telegram_user_id=telegram_user_id,
        )
        if car_reply is not None:
            return car_reply

        if text == "/start":
            return self.command_handlers.handle_start(chat_id=chat_id)
        if text == "/help":
            return self.command_handlers.handle_help(chat_id=chat_id)
        if text == "/addcar":
            return self.car_flow_handlers.start_add_car(chat_id=chat_id)
        if text == "/cars":
            return self.car_flow_handlers.list_cars(chat_id=chat_id)
        if text == "/addmaintenance":
            return self.maintenance_flow_handlers.start_add_maintenance(chat_id=chat_id)
        if text == "/addodometer":
            return self.odometer_flow_handlers.start_manual_update(chat_id=chat_id)

        return None
