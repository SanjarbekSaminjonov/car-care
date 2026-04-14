from bot.handlers.commands import BotReply
from selectors.car_selector import list_cars_for_chat
from services.car_service import create_car_for_chat
from services.conversation_state_service import clear_flow_state, get_flow_state, save_flow_state

FLOW_NAME = "car_add"


class CarFlowHandlers:
    def start_add_car(self, chat_id: int) -> BotReply:
        save_flow_state(
            chat_id=chat_id,
            flow_name=FLOW_NAME,
            state_name="awaiting_plate",
            state_payload={},
        )
        return BotReply(chat_id=chat_id, text="Davlat raqamini kiriting (masalan: 01A123BC):")

    def cancel(self, chat_id: int) -> BotReply:
        clear_flow_state(chat_id=chat_id, flow_name=FLOW_NAME)
        return BotReply(chat_id=chat_id, text="Joriy flow bekor qilindi.")

    def list_cars(self, chat_id: int) -> BotReply:
        cars = list_cars_for_chat(chat_id=chat_id)
        if not cars:
            return BotReply(chat_id=chat_id, text="Sizda hali mashina yo'q.")
        lines = ["Sizning mashinalaringiz:"]
        for car in cars:
            lines.append(f"- {car.plate_number} | {car.brand} {car.model} ({car.year})")
        return BotReply(chat_id=chat_id, text="\n".join(lines))

    def handle_flow_input(self, chat_id: int, text: str) -> BotReply | None:
        state = get_flow_state(chat_id=chat_id, flow_name=FLOW_NAME)
        if state is None:
            return None

        payload = dict(state.state_payload)

        if state.state_name == "awaiting_plate":
            payload["plate_number"] = text
            save_flow_state(
                chat_id=chat_id,
                flow_name=FLOW_NAME,
                state_name="awaiting_brand",
                state_payload=payload,
            )
            return BotReply(chat_id=chat_id, text="Brandni kiriting (masalan: Toyota):")

        if state.state_name == "awaiting_brand":
            payload["brand"] = text
            save_flow_state(
                chat_id=chat_id,
                flow_name=FLOW_NAME,
                state_name="awaiting_model",
                state_payload=payload,
            )
            return BotReply(chat_id=chat_id, text="Modelni kiriting (masalan: Corolla):")

        if state.state_name == "awaiting_model":
            payload["model"] = text
            save_flow_state(
                chat_id=chat_id,
                flow_name=FLOW_NAME,
                state_name="awaiting_year",
                state_payload=payload,
            )
            return BotReply(chat_id=chat_id, text="Yilni kiriting (masalan: 2022):")

        if state.state_name == "awaiting_year":
            if not text.isdigit():
                return BotReply(chat_id=chat_id, text="Yil raqam bo'lishi kerak. Qaytadan kiriting:")

            plate_number = payload.get("plate_number")
            brand = payload.get("brand")
            model = payload.get("model")
            if not isinstance(plate_number, str) or not isinstance(brand, str) or not isinstance(model, str):
                clear_flow_state(chat_id=chat_id, flow_name=FLOW_NAME)
                return BotReply(chat_id=chat_id, text="Flow xatosi. /addcar bilan qaytadan boshlang.")

            car = create_car_for_chat(
                chat_id=chat_id,
                plate_number=plate_number,
                brand=brand,
                model=model,
                year=int(text),
            )
            clear_flow_state(chat_id=chat_id, flow_name=FLOW_NAME)
            return BotReply(
                chat_id=chat_id,
                text=f"Mashina qo'shildi: {car.plate_number} ({car.brand} {car.model}, {car.year})",
            )

        return None
