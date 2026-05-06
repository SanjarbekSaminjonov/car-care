from dataclasses import dataclass

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.maintenance.models import (
    MaintenanceMediaAttachment,
    MaintenanceMediaType,
    MaintenanceRecord,
    MaintenanceStatus,
)
from apps.cars.models import Car, MembershipRole, MembershipStatus
from policies.car_access import assert_user_can_manage_car
from services.audit_service import log_audit_event
from services.telegram_account_service import get_telegram_account_for_chat


@dataclass(frozen=True)
class TelegramMediaPayload:
    media_type: str
    file_id: str
    file_unique_id: str = ""
    file_name: str = ""
    mime_type: str = ""
    file_size: int | None = None
    caption: str = ""


def _validate_media_payload(media: TelegramMediaPayload) -> None:
    if media.media_type not in {
        MaintenanceMediaType.IMAGE,
        MaintenanceMediaType.VIDEO,
        MaintenanceMediaType.DOCUMENT,
        MaintenanceMediaType.AUDIO,
    }:
        raise ValidationError("Unsupported media type.")
    if not media.file_id.strip():
        raise ValidationError("Telegram file_id is required.")
    if media.file_size is not None and media.file_size < 0:
        raise ValidationError("File size cannot be negative.")


def _latest_accessible_record(*, user_id, plate_number: str = "") -> MaintenanceRecord:
    records = MaintenanceRecord.objects.select_related("car").filter(
        car__memberships__user_id=user_id,
        car__memberships__status=MembershipStatus.ACTIVE,
        car__memberships__role__in=(MembershipRole.OWNER, MembershipRole.MANAGER),
        status=MaintenanceStatus.FINAL,
    )
    if plate_number.strip():
        records = records.filter(car__normalized_plate_number=Car.normalize_plate(plate_number))
    record = records.distinct().order_by("-event_date", "-created_at").first()
    if record is None:
        raise MaintenanceRecord.DoesNotExist("No maintenance record found for media attachment.")
    return record


@transaction.atomic
def attach_maintenance_media_for_chat(
    *,
    chat_id: int,
    telegram_user_id: int,
    media: TelegramMediaPayload,
    maintenance_record_id: str | None = None,
    plate_number: str = "",
) -> MaintenanceMediaAttachment:
    _validate_media_payload(media)
    telegram_account = get_telegram_account_for_chat(
        chat_id=chat_id,
        telegram_user_id=telegram_user_id,
    )

    if maintenance_record_id:
        record = MaintenanceRecord.objects.select_related("car").get(pk=maintenance_record_id)
    else:
        record = _latest_accessible_record(
            user_id=telegram_account.user_id,
            plate_number=plate_number,
        )

    assert_user_can_manage_car(user=telegram_account.user, car=record.car)

    attachment = MaintenanceMediaAttachment.objects.create(
        maintenance_record=record,
        media_type=media.media_type,
        telegram_file_id=media.file_id.strip(),
        telegram_file_unique_id=media.file_unique_id.strip(),
        file_name=media.file_name.strip(),
        mime_type=media.mime_type.strip(),
        file_size=media.file_size,
        caption=media.caption.strip(),
        uploaded_by=telegram_account.user,
    )
    log_audit_event(
        action="maintenance.media_attached",
        actor=telegram_account.user,
        entity=attachment,
        car=record.car,
        context={"source": "telegram", "chat_id": chat_id},
        metadata={
            "maintenance_record_id": str(record.id),
            "media_type": attachment.media_type,
            "file_name": attachment.file_name,
        },
    )
    return attachment
