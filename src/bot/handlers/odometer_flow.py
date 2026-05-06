from django.core.exceptions import ValidationError

from apps.cars.models import Car
from apps.telegram.models import TelegramAccount
from bot.handlers.car_selection import format_manageable_car_choices, resolve_selected_car
from bot.handlers.commands import BotReply
from bot.handlers.errors import format_validation_error
from bot.keyboards.inline import (
    ODOMETER_CANCEL_CALLBACK,
    ODOMETER_CONFIRM_CALLBACK,
    build_confirmation_keyboard,
)
from policies.car_access import CarAccessDenied
from queries.car_selector import list_manageable_cars_for_chat
from services.conversation_state_service import clear_flow_state, get_flow_state, save_flow_state
from services.odometer_service import create_odometer_for_chat

FLOW_NAME = "odometer_manual"
ACTION_LABEL = "Odometr yangilash"


class OdometerFlowHandlers:
    def start_manual_update(self, chat_id: int) -> BotReply:
        cars = list_manageable_cars_for_chat(chat_id=chat_id)
        if not cars:
            return BotReply(
                chat_id=chat_id,
                text="Odometr yangilash uchun sizda owner/manager huquqli mashina yo'q.",
            )
        if len(cars) == 1:
            save_flow_state(
                chat_id=chat_id,
                flow_name=FLOW_NAME,
                state_name="awaiting_value",
                state_payload={"plate_number": cars[0].plate_number},
            )
            return BotReply(
                chat_id=chat_id,
                text=f"{cars[0].plate_number} uchun odometr qiymatini kiriting:",
            )

        save_flow_state(
            chat_id=chat_id,
            flow_name=FLOW_NAME,
            state_name="awaiting_car_selection",
            state_payload={},
        )
        return BotReply(
            chat_id=chat_id,
            text=format_manageable_car_choices(cars, action_label=ACTION_LABEL),
        )

    def cancel(self, chat_id: int) -> None:
        clear_flow_state(chat_id=chat_id, flow_name=FLOW_NAME)

    def handle_flow_input(self, chat_id: int, text: str, telegram_user_id: int | None = None) -> BotReply | None:
        state = get_flow_state(chat_id=chat_id, flow_name=FLOW_NAME)
        if state is None:
            return None

        payload = dict(state.state_payload)

        if state.state_name == "awaiting_car_selection":
            cars = list_manageable_cars_for_chat(chat_id=chat_id)
            car = resolve_selected_car(cars, text)
            if car is None:
                if not cars:
                    clear_flow_state(chat_id=chat_id, flow_name=FLOW_NAME)
                    return BotReply(
                        chat_id=chat_id,
                        text="Odometr yangilash uchun sizda owner/manager huquqli mashina yo'q.",
                    )
                return BotReply(
                    chat_id=chat_id,
                    text=(
                        "Tanlov topilmadi.\n"
                        + format_manageable_car_choices(cars, action_label=ACTION_LABEL)
                    ),
                )
            payload["plate_number"] = car.plate_number
            save_flow_state(
                chat_id=chat_id,
                flow_name=FLOW_NAME,
                state_name="awaiting_value",
                state_payload=payload,
            )
            return BotReply(
                chat_id=chat_id,
                text=f"{car.plate_number} uchun odometr qiymatini kiriting:",
            )

        if state.state_name == "awaiting_plate":
            payload["plate_number"] = text
            save_flow_state(
                chat_id=chat_id,
                flow_name=FLOW_NAME,
                state_name="awaiting_value",
                state_payload=payload,
            )
            return BotReply(chat_id=chat_id, text=f"{text} uchun odometr qiymatini kiriting:")

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
                    f"- Odometr: {payload['value']}"
                ),
                reply_markup=build_confirmation_keyboard(
                    confirm_callback=ODOMETER_CONFIRM_CALLBACK,
                    cancel_callback=ODOMETER_CANCEL_CALLBACK,
                ),
            )

        if state.state_name == "awaiting_confirm":
            if text == ODOMETER_CANCEL_CALLBACK:
                clear_flow_state(chat_id=chat_id, flow_name=FLOW_NAME)
                return BotReply(chat_id=chat_id, text="Odometr yangilash bekor qilindi.")
            if text != ODOMETER_CONFIRM_CALLBACK:
                return BotReply(
                    chat_id=chat_id,
                    text="Tasdiqlash uchun pastdagi tugmalardan foydalaning yoki /cancel qiling.",
                    reply_markup=build_confirmation_keyboard(
                        confirm_callback=ODOMETER_CONFIRM_CALLBACK,
                        cancel_callback=ODOMETER_CANCEL_CALLBACK,
                    ),
                )
            if telegram_user_id is None:
                return BotReply(chat_id=chat_id, text="Telegram foydalanuvchi aniqlanmadi. /start bilan qayta urinib ko'ring.")

            plate_number = payload.get("plate_number")
            value = payload.get("value")
            if not isinstance(plate_number, str) or not isinstance(value, int):
                clear_flow_state(chat_id=chat_id, flow_name=FLOW_NAME)
                return BotReply(chat_id=chat_id, text="Flow xatosi. /addodometer bilan qayta boshlang.")

            try:
                entry = create_odometer_for_chat(
                    chat_id=chat_id,
                    telegram_user_id=telegram_user_id,
                    plate_number=plate_number,
                    value=value,
                )
            except Car.DoesNotExist:
                return BotReply(chat_id=chat_id, text="Bu mashina topilmadi yoki sizda access yo'q.")
            except CarAccessDenied:
                return BotReply(chat_id=chat_id, text="Bu mashina odometrini o'zgartirish huquqingiz yo'q.")
            except ValidationError as exc:
                return BotReply(chat_id=chat_id, text=format_validation_error(exc))
            except TelegramAccount.DoesNotExist:
                return BotReply(
                    chat_id=chat_id,
                    text="Telegram account topilmadi. /start bilan qayta urinib ko'ring.",
                )
            clear_flow_state(chat_id=chat_id, flow_name=FLOW_NAME)
            return BotReply(
                chat_id=chat_id,
                text=f"Odometr saqlandi: {entry.car.plate_number} -> {entry.value} km",
            )

        return None
