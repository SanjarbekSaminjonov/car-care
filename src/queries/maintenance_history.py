from django.db.models import Count

from apps.cars.models import Car, MembershipStatus
from apps.maintenance.models import MaintenanceRecord, MaintenanceStatus
from apps.telegram.models import TelegramAccount


def list_maintenance_history_for_chat(
    *,
    chat_id: int,
    plate_number: str = "",
    limit: int = 10,
) -> list[MaintenanceRecord]:
    if limit <= 0:
        return []

    telegram_account = TelegramAccount.objects.only("user_id").filter(chat_id=chat_id).first()
    if telegram_account is None:
        return []

    records = (
        MaintenanceRecord.objects.select_related("car", "created_by", "paid_by_user")
        .prefetch_related("line_items")
        .filter(
            car__memberships__user_id=telegram_account.user_id,
            car__memberships__status=MembershipStatus.ACTIVE,
            status=MaintenanceStatus.FINAL,
        )
        .annotate(media_count=Count("media_attachments", distinct=True))
    )

    if plate_number.strip():
        records = records.filter(car__normalized_plate_number=Car.normalize_plate(plate_number))

    return list(records.distinct().order_by("-event_date", "-created_at")[:limit])
