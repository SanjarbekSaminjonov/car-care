from django.utils import timezone

from apps.cars.models import Car
from apps.odometer.models import OdometerEntry, OdometerSource
from services.telegram_account_service import get_telegram_account_for_chat


def create_odometer_for_chat(*, chat_id: int, plate_number: str, value: int) -> OdometerEntry:
    telegram_account = get_telegram_account_for_chat(chat_id=chat_id)
    normalized_plate = Car.normalize_plate(plate_number)

    car = Car.objects.get(
        normalized_plate_number=normalized_plate,
        memberships__user_id=telegram_account.user_id,
    )

    return OdometerEntry.objects.create(
        car=car,
        value=value,
        entry_date=timezone.localdate(),
        source=OdometerSource.MANUAL,
        created_by=telegram_account.user,
    )
