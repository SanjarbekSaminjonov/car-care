from bot.handlers.commands import BotReply
from services.conversation_state_service import clear_flow_state, get_flow_state, save_flow_state
from services.odometer_service import create_odometer_for_chat

FLOW_NAME = "odometer_manual"


class OdometerFlowHandlers:
    def start_manual_update(self, chat_id: int) -> BotReply:
        save_flow_state(
            chat_id=chat_id,
            flow_name=FLOW_NAME,
            state_name="awaiting_plate",
            state_payload={},
        )
        return BotReply(chat_id=chat_id, text="Davlat raqamini kiriting:")

    def cancel(self, chat_id: int) -> None:
        clear_flow_state(chat_id=chat_id, flow_name=FLOW_NAME)

    def handle_flow_input(self, chat_id: int, text: str, telegram_user_id: int | None = None) -> BotReply | None:
        state = get_flow_state(chat_id=chat_id, flow_name=FLOW_NAME)
        if state is None:
            return None

        payload = dict(state.state_payload)

        if state.state_name == "awaiting_plate":
            payload["plate_number"] = text
            save_flow_state(
                chat_id=chat_id,
                flow_name=FLOW_NAME,
                state_name="awaiting_value",
                state_payload=payload,
            )
            return BotReply(chat_id=chat_id, text="Odometr qiymatini kiriting:")

        if state.state_name == "awaiting_value":
            if not text.isdigit():
                return BotReply(chat_id=chat_id, text="Odometr faqat raqam bo'lishi kerak.")

            payload["value"] = int(text)
            save_flow_state(
                chat_id=chat_id,
                flow_name=FLOW_NAME,
                state_name="awaiting_confirm",
                state_payload=payload,
            )
            return BotReply(
                chat_id=chat_id,
                text=(
                    "Tasdiqlang:\n"
                    f"- Mashina: {payload['plate_number']}\n"
                    f"- Odometr: {payload['value']}\n"
                    "Tasdiqlash uchun: yes"
                ),
            )

        if state.state_name == "awaiting_confirm":
            if text.lower() != "yes":
                return BotReply(chat_id=chat_id, text="Tasdiqlash uchun 'yes' deb yozing yoki /cancel qiling.")
            if telegram_user_id is None:
                return BotReply(chat_id=chat_id, text="Telegram foydalanuvchi aniqlanmadi. /start bilan qayta urinib ko'ring.")

            plate_number = payload.get("plate_number")
            value = payload.get("value")
            if not isinstance(plate_number, str) or not isinstance(value, int):
                clear_flow_state(chat_id=chat_id, flow_name=FLOW_NAME)
                return BotReply(chat_id=chat_id, text="Flow xatosi. /addodometer bilan qayta boshlang.")

            entry = create_odometer_for_chat(
                chat_id=chat_id,
                telegram_user_id=telegram_user_id,
                plate_number=plate_number,
                value=value,
            )
            clear_flow_state(chat_id=chat_id, flow_name=FLOW_NAME)
            return BotReply(
                chat_id=chat_id,
                text=f"Odometr saqlandi: {entry.car.plate_number} -> {entry.value} km",
            )

        return None
