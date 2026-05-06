from django.core.exceptions import ValidationError

from apps.cars.models import Car, CarInviteToken
from apps.telegram.models import TelegramAccount
from bot.handlers.commands import BotReply
from bot.handlers.errors import format_validation_error
from policies.car_access import CarAccessDenied
from services.car_invite_service import (
    CarInviteError,
    accept_car_invite_for_chat,
    create_car_invite_for_chat,
)
from services.conversation_state_service import clear_flow_state, get_flow_state, save_flow_state

FLOW_NAME = "car_share"


class ShareFlowHandlers:
    def start_share(
        self,
        *,
        chat_id: int,
        telegram_user_id: int | None,
        args: str = "",
    ) -> BotReply:
        parts = args.split()
        if len(parts) >= 2:
            return self._create_invite(
                chat_id=chat_id,
                telegram_user_id=telegram_user_id,
                plate_number=parts[0],
                role=parts[1],
            )

        if len(parts) == 1:
            save_flow_state(
                chat_id=chat_id,
                flow_name=FLOW_NAME,
                state_name="awaiting_role",
                state_payload={"plate_number": parts[0]},
            )
            return BotReply(chat_id=chat_id, text="Qaysi rol? viewer yoki manager deb yozing.")

        save_flow_state(
            chat_id=chat_id,
            flow_name=FLOW_NAME,
            state_name="awaiting_plate",
            state_payload={},
        )
        return BotReply(chat_id=chat_id, text="Qaysi mashina? Davlat raqamini kiriting:")

    def accept_invite(
        self,
        *,
        chat_id: int,
        telegram_user_id: int | None,
        token: str,
    ) -> BotReply:
        if telegram_user_id is None:
            return BotReply(
                chat_id=chat_id,
                text="Telegram foydalanuvchi aniqlanmadi. /start bilan qayta urinib ko'ring.",
            )

        try:
            result = accept_car_invite_for_chat(
                chat_id=chat_id,
                telegram_user_id=telegram_user_id,
                token=token,
            )
        except CarInviteToken.DoesNotExist:
            return BotReply(chat_id=chat_id, text="Invite topilmadi yoki noto'g'ri.")
        except (CarInviteError, ValidationError) as exc:
            return BotReply(chat_id=chat_id, text=format_validation_error(exc))
        except TelegramAccount.DoesNotExist:
            return BotReply(
                chat_id=chat_id,
                text="Telegram account topilmadi. /start bilan qayta urinib ko'ring.",
            )

        car = result.invite.car
        return BotReply(
            chat_id=chat_id,
            text=(
                f"Siz {car.plate_number} ({car.brand} {car.model}) mashinasiga "
                f"{result.membership.role} sifatida qo'shildingiz."
            ),
        )

    def cancel(self, chat_id: int) -> None:
        clear_flow_state(chat_id=chat_id, flow_name=FLOW_NAME)

    def handle_flow_input(
        self,
        *,
        chat_id: int,
        text: str,
        telegram_user_id: int | None = None,
    ) -> BotReply | None:
        state = get_flow_state(chat_id=chat_id, flow_name=FLOW_NAME)
        if state is None:
            return None

        payload = dict(state.state_payload)
        if state.state_name == "awaiting_plate":
            payload["plate_number"] = text
            save_flow_state(
                chat_id=chat_id,
                flow_name=FLOW_NAME,
                state_name="awaiting_role",
                state_payload=payload,
            )
            return BotReply(chat_id=chat_id, text="Qaysi rol? viewer yoki manager deb yozing.")

        if state.state_name == "awaiting_role":
            clear_flow_state(chat_id=chat_id, flow_name=FLOW_NAME)
            plate_number = payload.get("plate_number")
            if not isinstance(plate_number, str):
                return BotReply(chat_id=chat_id, text="Flow xatosi. /share bilan qayta boshlang.")
            return self._create_invite(
                chat_id=chat_id,
                telegram_user_id=telegram_user_id,
                plate_number=plate_number,
                role=text,
            )

        return None

    def _create_invite(
        self,
        *,
        chat_id: int,
        telegram_user_id: int | None,
        plate_number: str,
        role: str,
    ) -> BotReply:
        if telegram_user_id is None:
            return BotReply(
                chat_id=chat_id,
                text="Telegram foydalanuvchi aniqlanmadi. /start bilan qayta urinib ko'ring.",
            )

        try:
            invite = create_car_invite_for_chat(
                chat_id=chat_id,
                telegram_user_id=telegram_user_id,
                plate_number=plate_number,
                role=role,
            )
        except Car.DoesNotExist:
            return BotReply(chat_id=chat_id, text="Bu mashina topilmadi yoki sizda access yo'q.")
        except CarAccessDenied:
            return BotReply(chat_id=chat_id, text="Faqat owner mashinani ulasha oladi.")
        except (CarInviteError, ValidationError) as exc:
            return BotReply(chat_id=chat_id, text=format_validation_error(exc))
        except TelegramAccount.DoesNotExist:
            return BotReply(
                chat_id=chat_id,
                text="Telegram account topilmadi. /start bilan qayta urinib ko'ring.",
            )

        return BotReply(
            chat_id=chat_id,
            text=(
                "Invite tayyor.\n"
                f"Mashina: {invite.car.plate_number} ({invite.car.brand} {invite.car.model})\n"
                f"Rol: {invite.role}\n"
                f"Muddati: {invite.expires_at:%Y-%m-%d %H:%M} UTC\n\n"
                "Ulashish kodi:\n"
                f"/join {invite.token}"
            ),
        )
