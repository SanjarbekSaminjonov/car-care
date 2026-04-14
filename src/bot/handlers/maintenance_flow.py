from decimal import Decimal, InvalidOperation

from bot.handlers.commands import BotReply
from services.conversation_state_service import clear_flow_state, get_flow_state, save_flow_state
from services.maintenance_service import create_maintenance_for_chat

FLOW_NAME = "maintenance_add"


class MaintenanceFlowHandlers:

    def start_add_maintenance(self, chat_id: int) -> BotReply:
        save_flow_state(chat_id=chat_id, flow_name=FLOW_NAME, state_name="awaiting_plate", state_payload={})
        return BotReply(chat_id=chat_id, text="Qaysi mashina uchun? Davlat raqamini kiriting:")

    def cancel(self, chat_id: int) -> None:
        clear_flow_state(chat_id=chat_id, flow_name=FLOW_NAME)

    def handle_flow_input(self, chat_id: int, text: str) -> BotReply | None:
        state = get_flow_state(chat_id=chat_id, flow_name=FLOW_NAME)
        if state is None:
            return None

        payload = dict(state.state_payload)

        if state.state_name == "awaiting_plate":
            payload["plate_number"] = text
            save_flow_state(chat_id=chat_id, flow_name=FLOW_NAME, state_name="awaiting_title", state_payload=payload)
            return BotReply(chat_id=chat_id, text="Servis nomini kiriting (masalan: Oil change):")

        if state.state_name == "awaiting_title":
            payload["title"] = text
            save_flow_state(chat_id=chat_id, flow_name=FLOW_NAME, state_name="awaiting_odometer", state_payload=payload)
            return BotReply(chat_id=chat_id, text="Odometr qiymatini kiriting:")

        if state.state_name == "awaiting_odometer":
            if not text.isdigit():
                return BotReply(chat_id=chat_id, text="Odometr faqat raqam bo'lishi kerak.")
            payload["odometer"] = int(text)
            save_flow_state(chat_id=chat_id, flow_name=FLOW_NAME, state_name="awaiting_item_name", state_payload=payload)
            return BotReply(chat_id=chat_id, text="Line item nomini kiriting:")

        if state.state_name == "awaiting_item_name":
            payload["item_name"] = text
            save_flow_state(chat_id=chat_id, flow_name=FLOW_NAME, state_name="awaiting_item_amount", state_payload=payload)
            return BotReply(chat_id=chat_id, text="Line item summasini kiriting (masalan: 150000):")

        if state.state_name == "awaiting_item_amount":
            try:
                Decimal(text)
            except InvalidOperation:
                return BotReply(chat_id=chat_id, text="Summa son bo'lishi kerak.")

            payload["item_amount"] = text
            save_flow_state(chat_id=chat_id, flow_name=FLOW_NAME, state_name="awaiting_confirm", state_payload=payload)
            summary = (
                "Tasdiqlang:\n"
                f"- Mashina: {payload.get('plate_number')}\n"
                f"- Servis: {payload.get('title')}\n"
                f"- Odometr: {payload.get('odometer')}\n"
                f"- Item: {payload.get('item_name')}\n"
                f"- Summa: {payload.get('item_amount')}\n"
                "Tasdiqlash uchun: yes"
            )
            return BotReply(chat_id=chat_id, text=summary)

        if state.state_name == "awaiting_confirm":
            if text.lower() != "yes":
                return BotReply(chat_id=chat_id, text="Tasdiqlash uchun 'yes' deb yozing yoki /cancel qiling.")

            plate_number = payload.get("plate_number")
            title = payload.get("title")
            odometer = payload.get("odometer")
            item_name = payload.get("item_name")
            item_amount = payload.get("item_amount")
            if (
                not isinstance(plate_number, str)
                or not isinstance(title, str)
                or not isinstance(odometer, int)
                or not isinstance(item_name, str)
                or not isinstance(item_amount, str)
            ):
                clear_flow_state(chat_id=chat_id, flow_name=FLOW_NAME)
                return BotReply(chat_id=chat_id, text="Flow xatosi. /addmaintenance bilan qayta boshlang.")

            record = create_maintenance_for_chat(
                chat_id=chat_id,
                plate_number=plate_number,
                title=title,
                odometer=odometer,
                item_name=item_name,
                item_amount=Decimal(item_amount),
            )
            clear_flow_state(chat_id=chat_id, flow_name=FLOW_NAME)
            return BotReply(
                chat_id=chat_id,
                text=f"Servis yozuvi saqlandi: {record.car.plate_number} | {record.title}",
            )

        return None
