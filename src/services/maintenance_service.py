from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.cars.models import Car
from apps.maintenance.models import (
    MaintenanceItemType,
    MaintenanceLineItem,
    MaintenanceRecord,
    MaintenanceStatus,
)
from services.telegram_account_service import get_telegram_account_for_chat


@transaction.atomic
def create_maintenance_for_chat(
    *,
    chat_id: int,
    plate_number: str,
    title: str,
    odometer: int,
    item_name: str,
    item_amount: Decimal,
) -> MaintenanceRecord:
    telegram_account = get_telegram_account_for_chat(chat_id=chat_id)

    normalized_plate = Car.normalize_plate(plate_number)
    car = Car.objects.get(
        normalized_plate_number=normalized_plate,
        memberships__user_id=telegram_account.user_id,
    )

    record = MaintenanceRecord.objects.create(
        car=car,
        event_date=timezone.localdate(),
        odometer=odometer,
        title=title,
        description="Created from Telegram bot",
        created_by=telegram_account.user,
        paid_by_user=telegram_account.user,
        status=MaintenanceStatus.FINAL,
    )

    MaintenanceLineItem.objects.create(
        maintenance_record=record,
        item_type=MaintenanceItemType.SERVICE,
        name=item_name,
        quantity=1,
        unit_price=item_amount,
        total_price=item_amount,
        paid_by_user=telegram_account.user,
    )

    return record
