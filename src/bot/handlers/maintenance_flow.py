from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.cars.models import Car
from apps.maintenance.models import MaintenanceMediaType, MaintenanceRecord
from apps.telegram.models import TelegramAccount
from bot.formatters.messages import format_maintenance_history
from bot.handlers.car_selection import format_manageable_car_choices, resolve_selected_car
from bot.handlers.commands import BotReply
from bot.handlers.errors import format_validation_error
from bot.keyboards.inline import (
    MAINTENANCE_CANCEL_CALLBACK,
    MAINTENANCE_CONFIRM_CALLBACK,
    MAINTENANCE_DATE_TODAY_CALLBACK,
    build_confirmation_keyboard,
    build_today_date_keyboard,
)
from policies.car_access import CarAccessDenied
from queries.car_selector import list_manageable_cars_for_chat
from queries.maintenance_history import list_maintenance_history_for_chat
from services.conversation_state_service import clear_flow_state, get_flow_state, save_flow_state
from services.maintenance_media_service import TelegramMediaPayload, attach_maintenance_media_for_chat
from services.maintenance_service import create_maintenance_for_chat

FLOW_NAME = "maintenance_add"
MEDIA_FLOW_NAME = "maintenance_media_attach"
ACTION_LABEL = "Servis yozuvi qo'shish"
DATE_FORMATS = ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y")


class MaintenanceFlowHandlers:

    def start_add_maintenance(self, chat_id: int) -> BotReply:
        cars = list_manageable_cars_for_chat(chat_id=chat_id)
        if not cars:
            return BotReply(
                chat_id=chat_id,
                text="Servis yozuvi qo'shish uchun sizda owner/manager huquqli mashina yo'q.",
            )
        if len(cars) == 1:
            save_flow_state(
                chat_id=chat_id,
                flow_name=FLOW_NAME,
                state_name="awaiting_title",
                state_payload={"plate_number": cars[0].plate_number},
            )
            return BotReply(
                chat_id=chat_id,
                text=f"{cars[0].plate_number} uchun servis nomini kiriting (masalan: Oil change):",
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
        clear_flow_state(chat_id=chat_id, flow_name=MEDIA_FLOW_NAME)

    def show_history(self, *, chat_id: int, plate_number: str = "") -> BotReply:
        records = list_maintenance_history_for_chat(
            chat_id=chat_id,
            plate_number=plate_number,
            limit=10,
        )
        return BotReply(chat_id=chat_id, text=format_maintenance_history(records))

    def start_attach_media(self, *, chat_id: int, plate_number: str = "") -> BotReply:
        save_flow_state(
            chat_id=chat_id,
            flow_name=MEDIA_FLOW_NAME,
            state_name="awaiting_media",
            state_payload={"plate_number": plate_number.strip()},
        )
        target = f" {plate_number.strip()}" if plate_number.strip() else ""
        return BotReply(
            chat_id=chat_id,
            text=f"Oxirgi servis yozuviga media biriktirish uchun rasm/video/audio/hujjat yuboring{target}. /skip bilan o'tkazib yuborish mumkin.",
        )

    def handle_flow_input(self, chat_id: int, text: str, telegram_user_id: int | None = None) -> BotReply | None:
        state = get_flow_state(chat_id=chat_id, flow_name=FLOW_NAME)
        if state is None:
            media_state = get_flow_state(chat_id=chat_id, flow_name=MEDIA_FLOW_NAME)
            if media_state is None:
                return None
            if text.lower() in {"/skip", "skip", "yo'q", "yoq", "no"}:
                clear_flow_state(chat_id=chat_id, flow_name=MEDIA_FLOW_NAME)
                return BotReply(chat_id=chat_id, text="Media biriktirish o'tkazib yuborildi.")
            return BotReply(
                chat_id=chat_id,
                text="Media yuboring: rasm, video, audio yoki hujjat. O'tkazib yuborish uchun /skip.",
            )

        payload = dict(state.state_payload)

        if state.state_name == "awaiting_car_selection":
            cars = list_manageable_cars_for_chat(chat_id=chat_id)
            car = resolve_selected_car(cars, text)
            if car is None:
                if not cars:
                    clear_flow_state(chat_id=chat_id, flow_name=FLOW_NAME)
                    return BotReply(
                        chat_id=chat_id,
                        text="Servis yozuvi qo'shish uchun sizda owner/manager huquqli mashina yo'q.",
                    )
                return BotReply(
                    chat_id=chat_id,
                    text=(
                        "Tanlov topilmadi.\n"
                        + format_manageable_car_choices(cars, action_label=ACTION_LABEL)
                    ),
                )
            payload["plate_number"] = car.plate_number
            save_flow_state(chat_id=chat_id, flow_name=FLOW_NAME, state_name="awaiting_title", state_payload=payload)
            return BotReply(
                chat_id=chat_id,
                text=f"{car.plate_number} uchun servis nomini kiriting (masalan: Oil change):",
            )

        if state.state_name == "awaiting_plate":
            payload["plate_number"] = text
            save_flow_state(chat_id=chat_id, flow_name=FLOW_NAME, state_name="awaiting_title", state_payload=payload)
            return BotReply(chat_id=chat_id, text=f"{text} uchun servis nomini kiriting (masalan: Oil change):")

        if state.state_name == "awaiting_title":
            payload["title"] = text
            save_flow_state(chat_id=chat_id, flow_name=FLOW_NAME, state_name="awaiting_event_date", state_payload=payload)
            return BotReply(
                chat_id=chat_id,
                text=(
                    "Servis qachon qilingan?\n"
                    "Bugun bo'lsa tugmani bosing, oldinroq bo'lsa sanani yozing "
                    "(masalan: 2026-04-20 yoki 20.04.2026)."
                ),
                reply_markup=build_today_date_keyboard(),
            )

        if state.state_name == "awaiting_event_date":
            event_date = self._resolve_event_date(text)
            if event_date is None:
                return BotReply(
                    chat_id=chat_id,
                    text=(
                        "Sana tushunarsiz. Bugun bo'lsa tugmani bosing yoki sanani "
                        "2026-04-20 / 20.04.2026 formatida yuboring."
                    ),
                    reply_markup=build_today_date_keyboard(),
                )
            if event_date > timezone.localdate():
                return BotReply(
                    chat_id=chat_id,
                    text="Servis sanasi kelajakda bo'lishi mumkin emas. Qaytadan kiriting.",
                    reply_markup=build_today_date_keyboard(),
                )

            payload["event_date"] = event_date.isoformat()
            save_flow_state(chat_id=chat_id, flow_name=FLOW_NAME, state_name="awaiting_odometer", state_payload=payload)
            return BotReply(
                chat_id=chat_id,
                text=f"Servis sanasi: {event_date:%Y-%m-%d}\nOdometr qiymatini kiriting:",
            )

        if state.state_name == "awaiting_odometer":
            if not text.isdigit():
                return BotReply(chat_id=chat_id, text="Odometr faqat raqam bo'lishi kerak.")
            payload["odometer"] = int(text)
            save_flow_state(chat_id=chat_id, flow_name=FLOW_NAME, state_name="awaiting_item_name", state_payload=payload)
            return BotReply(
                chat_id=chat_id,
                text="Servis xarajati nomini kiriting (masalan: motor moyi, moy filtri, ish haqi):",
            )

        if state.state_name == "awaiting_item_name":
            payload["item_name"] = text
            save_flow_state(chat_id=chat_id, flow_name=FLOW_NAME, state_name="awaiting_item_amount", state_payload=payload)
            return BotReply(chat_id=chat_id, text="Shu xarajat summasini kiriting (masalan: 150000):")

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
                f"- Sana: {payload.get('event_date')}\n"
                f"- Odometr: {payload.get('odometer')}\n"
                f"- Xarajat: {payload.get('item_name')}\n"
                f"- Summa: {payload.get('item_amount')}"
            )
            return BotReply(
                chat_id=chat_id,
                text=summary,
                reply_markup=build_confirmation_keyboard(
                    confirm_callback=MAINTENANCE_CONFIRM_CALLBACK,
                    cancel_callback=MAINTENANCE_CANCEL_CALLBACK,
                ),
            )

        if state.state_name == "awaiting_confirm":
            if text == MAINTENANCE_CANCEL_CALLBACK:
                clear_flow_state(chat_id=chat_id, flow_name=FLOW_NAME)
                return BotReply(chat_id=chat_id, text="Servis yozuvi bekor qilindi.")
            if text != MAINTENANCE_CONFIRM_CALLBACK:
                return BotReply(
                    chat_id=chat_id,
                    text="Tasdiqlash uchun pastdagi tugmalardan foydalaning yoki /cancel qiling.",
                    reply_markup=build_confirmation_keyboard(
                        confirm_callback=MAINTENANCE_CONFIRM_CALLBACK,
                        cancel_callback=MAINTENANCE_CANCEL_CALLBACK,
                    ),
                )
            if telegram_user_id is None:
                return BotReply(chat_id=chat_id, text="Telegram foydalanuvchi aniqlanmadi. /start bilan qayta urinib ko'ring.")

            plate_number = payload.get("plate_number")
            title = payload.get("title")
            event_date = payload.get("event_date")
            odometer = payload.get("odometer")
            item_name = payload.get("item_name")
            item_amount = payload.get("item_amount")
            if (
                not isinstance(plate_number, str)
                or not isinstance(title, str)
                or not isinstance(event_date, str)
                or not isinstance(odometer, int)
                or not isinstance(item_name, str)
                or not isinstance(item_amount, str)
            ):
                clear_flow_state(chat_id=chat_id, flow_name=FLOW_NAME)
                return BotReply(chat_id=chat_id, text="Flow xatosi. /addmaintenance bilan qayta boshlang.")

            try:
                record = create_maintenance_for_chat(
                    chat_id=chat_id,
                    telegram_user_id=telegram_user_id,
                    plate_number=plate_number,
                    title=title,
                    event_date=date.fromisoformat(event_date),
                    odometer=odometer,
                    item_name=item_name,
                    item_amount=Decimal(item_amount),
                )
            except Car.DoesNotExist:
                return BotReply(chat_id=chat_id, text="Bu mashina topilmadi yoki sizda access yo'q.")
            except CarAccessDenied:
                return BotReply(chat_id=chat_id, text="Bu mashinaga yozuv qo'shish huquqingiz yo'q.")
            except ValidationError as exc:
                return BotReply(chat_id=chat_id, text=format_validation_error(exc))
            except TelegramAccount.DoesNotExist:
                return BotReply(
                    chat_id=chat_id,
                    text="Telegram account topilmadi. /start bilan qayta urinib ko'ring.",
                )
            clear_flow_state(chat_id=chat_id, flow_name=FLOW_NAME)
            save_flow_state(
                chat_id=chat_id,
                flow_name=MEDIA_FLOW_NAME,
                state_name="awaiting_media",
                state_payload={"maintenance_record_id": str(record.id)},
            )
            return BotReply(
                chat_id=chat_id,
                text=(
                    f"Servis yozuvi saqlandi: {record.car.plate_number} | {record.title}\n"
                    "Rasm/video/audio/hujjat yuborsangiz shu servisga biriktiraman. "
                    "O'tkazib yuborish uchun /skip."
                ),
            )

        return None

    def _resolve_event_date(self, text: str) -> date | None:
        if text == MAINTENANCE_DATE_TODAY_CALLBACK:
            return timezone.localdate()

        normalized_text = text.strip()
        for date_format in DATE_FORMATS:
            try:
                return datetime.strptime(normalized_text, date_format).date()
            except ValueError:
                continue
        return None

    def handle_media_input(
        self,
        *,
        chat_id: int,
        message: dict,
        telegram_user_id: int | None = None,
    ) -> BotReply | None:
        state = get_flow_state(chat_id=chat_id, flow_name=MEDIA_FLOW_NAME)
        if state is None:
            return None
        if telegram_user_id is None:
            return BotReply(
                chat_id=chat_id,
                text="Telegram foydalanuvchi aniqlanmadi. /start bilan qayta urinib ko'ring.",
            )

        media = self._extract_media_payload(message)
        if media is None:
            return BotReply(
                chat_id=chat_id,
                text="Rasm, video, audio yoki hujjat yuboring. O'tkazib yuborish uchun /skip.",
            )

        payload = dict(state.state_payload)
        try:
            attachment = attach_maintenance_media_for_chat(
                chat_id=chat_id,
                telegram_user_id=telegram_user_id,
                media=media,
                maintenance_record_id=payload.get("maintenance_record_id"),
                plate_number=str(payload.get("plate_number") or ""),
            )
        except MaintenanceRecord.DoesNotExist:
            return BotReply(chat_id=chat_id, text="Media biriktirish uchun servis yozuvi topilmadi.")
        except CarAccessDenied:
            return BotReply(chat_id=chat_id, text="Bu servisga media biriktirish huquqingiz yo'q.")
        except ValidationError as exc:
            return BotReply(chat_id=chat_id, text=format_validation_error(exc))
        except TelegramAccount.DoesNotExist:
            return BotReply(
                chat_id=chat_id,
                text="Telegram account topilmadi. /start bilan qayta urinib ko'ring.",
            )

        clear_flow_state(chat_id=chat_id, flow_name=MEDIA_FLOW_NAME)
        label = attachment.file_name or attachment.media_type
        return BotReply(
            chat_id=chat_id,
            text=f"Media biriktirildi: {attachment.maintenance_record.car.plate_number} | {attachment.maintenance_record.title} | {label}",
        )

    def _extract_media_payload(self, message: dict) -> TelegramMediaPayload | None:
        caption = str(message.get("caption") or "")

        photos = message.get("photo")
        if isinstance(photos, list) and photos:
            photo = photos[-1]
            if isinstance(photo, dict):
                return TelegramMediaPayload(
                    media_type=MaintenanceMediaType.IMAGE,
                    file_id=str(photo.get("file_id") or ""),
                    file_unique_id=str(photo.get("file_unique_id") or ""),
                    file_size=photo.get("file_size") if isinstance(photo.get("file_size"), int) else None,
                    caption=caption,
                )

        for telegram_key, media_type in (
            ("document", MaintenanceMediaType.DOCUMENT),
            ("video", MaintenanceMediaType.VIDEO),
            ("audio", MaintenanceMediaType.AUDIO),
        ):
            raw_media = message.get(telegram_key)
            if isinstance(raw_media, dict):
                return TelegramMediaPayload(
                    media_type=media_type,
                    file_id=str(raw_media.get("file_id") or ""),
                    file_unique_id=str(raw_media.get("file_unique_id") or ""),
                    file_name=str(raw_media.get("file_name") or ""),
                    mime_type=str(raw_media.get("mime_type") or ""),
                    file_size=raw_media.get("file_size") if isinstance(raw_media.get("file_size"), int) else None,
                    caption=caption,
                )

        return None
