from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Max
from django.utils import timezone

from apps.cars.models import Car
from apps.odometer.models import OdometerEntry, OdometerSource
from policies.car_access import assert_user_can_manage_car
from queries.car_selector import get_active_car_for_user_by_plate
from services.audit_service import log_audit_event
from services.telegram_account_service import get_telegram_account_for_chat


@transaction.atomic
def register_odometer_entry(
    *,
    car: Car,
    user,
    value: int,
    source: str,
    entry_date=None,
    maintenance_record=None,
    enforce_monotonic: bool = True,
) -> OdometerEntry:
    if value <= 0:
        raise ValidationError("Odometer value must be positive.")

    locked_car = Car.objects.select_for_update().get(pk=car.pk)
    assert_user_can_manage_car(user=user, car=locked_car)

    cached_current_value = locked_car.current_odometer
    current_value = cached_current_value
    if cached_current_value is None:
        current_value = (
            OdometerEntry.objects.filter(car=locked_car).aggregate(max_value=Max("value"))[
                "max_value"
            ]
        )

    if enforce_monotonic and current_value is not None and value < current_value:
        raise ValidationError("Odometer value cannot be lower than the current odometer.")

    entry = OdometerEntry.objects.create(
        car=locked_car,
        maintenance_record=maintenance_record,
        value=value,
        entry_date=entry_date or timezone.localdate(),
        source=source,
        created_by=user,
    )

    next_current_value = value if current_value is None else max(current_value, value)
    if locked_car.current_odometer != next_current_value:
        locked_car.current_odometer = next_current_value
        locked_car.save(update_fields=["current_odometer", "updated_at"])

    log_audit_event(
        action="odometer.recorded",
        actor=user,
        entity=entry,
        car=locked_car,
        context={"source": source, "maintenance_record_id": str(maintenance_record.pk) if maintenance_record else ""},
        metadata={"value": value, "entry_date": str(entry.entry_date)},
    )

    return entry


@transaction.atomic
def create_odometer_for_chat(
    *, chat_id: int, telegram_user_id: int, plate_number: str, value: int
) -> OdometerEntry:
    telegram_account = get_telegram_account_for_chat(
        chat_id=chat_id,
        telegram_user_id=telegram_user_id,
    )
    car = get_active_car_for_user_by_plate(
        user_id=telegram_account.user_id,
        plate_number=plate_number,
    )
    return register_odometer_entry(
        car=car,
        user=telegram_account.user,
        value=value,
        source=OdometerSource.MANUAL,
    )
