from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.maintenance.models import (
    MaintenanceItemType,
    MaintenanceLineItem,
    MaintenanceRecord,
    MaintenanceStatus,
)
from apps.odometer.models import OdometerSource
from queries.car_selector import get_active_car_for_user_by_plate
from services.audit_service import log_audit_event
from services.odometer_service import register_odometer_entry
from services.telegram_account_service import get_telegram_account_for_chat


def _validate_maintenance_payload(
    *, title: str, event_date: date, odometer: int, item_name: str, item_amount: Decimal
) -> None:
    if not title.strip():
        raise ValidationError("Servis nomi kerak.")
    if event_date > timezone.localdate():
        raise ValidationError("Servis sanasi kelajakda bo'lishi mumkin emas.")
    if odometer <= 0:
        raise ValidationError("Odometr qiymati musbat bo'lishi kerak.")
    if not item_name.strip():
        raise ValidationError("Servis xarajati nomi kerak.")
    if item_amount <= 0:
        raise ValidationError("Xarajat summasi musbat bo'lishi kerak.")


@transaction.atomic
def create_maintenance_for_chat(
    *,
    chat_id: int,
    telegram_user_id: int,
    plate_number: str,
    title: str,
    odometer: int,
    item_name: str,
    item_amount: Decimal,
    event_date: date | None = None,
) -> MaintenanceRecord:
    service_date = event_date or timezone.localdate()
    _validate_maintenance_payload(
        title=title,
        event_date=service_date,
        odometer=odometer,
        item_name=item_name,
        item_amount=item_amount,
    )
    telegram_account = get_telegram_account_for_chat(
        chat_id=chat_id,
        telegram_user_id=telegram_user_id,
    )

    car = get_active_car_for_user_by_plate(
        user_id=telegram_account.user_id,
        plate_number=plate_number,
    )

    record = MaintenanceRecord.objects.create(
        car=car,
        event_date=service_date,
        odometer=odometer,
        title=title.strip(),
        description="Created from Telegram bot",
        total_amount=item_amount,
        created_by=telegram_account.user,
        paid_by_user=telegram_account.user,
        status=MaintenanceStatus.FINAL,
    )

    MaintenanceLineItem.objects.create(
        maintenance_record=record,
        item_type=MaintenanceItemType.SERVICE,
        name=item_name.strip(),
        quantity=1,
        unit_price=item_amount,
        total_price=item_amount,
        paid_by_user=telegram_account.user,
    )

    register_odometer_entry(
        car=car,
        user=telegram_account.user,
        value=odometer,
        source=OdometerSource.MAINTENANCE_RECORD,
        entry_date=record.event_date,
        maintenance_record=record,
        enforce_monotonic=False,
    )
    log_audit_event(
        action="maintenance.created",
        actor=telegram_account.user,
        entity=record,
        car=car,
        context={"source": "telegram", "chat_id": chat_id},
        metadata={
            "title": record.title,
            "event_date": str(record.event_date),
            "odometer": odometer,
            "total_amount": str(item_amount),
        },
    )

    return record
