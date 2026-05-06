from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.cars.models import Car, CarMembership, MembershipRole, MembershipStatus
from services.audit_service import log_audit_event
from services.telegram_account_service import get_telegram_account_for_chat


def _validate_car_payload(*, plate_number: str, brand: str, model: str, year: int) -> None:
    if not plate_number.strip():
        raise ValidationError("Plate number is required.")
    if not brand.strip():
        raise ValidationError("Brand is required.")
    if not model.strip():
        raise ValidationError("Model is required.")

    current_year = timezone.localdate().year
    if year < 1886 or year > current_year + 1:
        raise ValidationError("Car year is outside the supported range.")


@transaction.atomic
def create_car_for_chat(
    *, chat_id: int, telegram_user_id: int, plate_number: str, brand: str, model: str, year: int
) -> Car:
    _validate_car_payload(plate_number=plate_number, brand=brand, model=model, year=year)
    telegram_account = get_telegram_account_for_chat(
        chat_id=chat_id,
        telegram_user_id=telegram_user_id,
    )

    car = Car.objects.create(
        plate_number=plate_number.strip(),
        normalized_plate_number=Car.normalize_plate(plate_number),
        brand=brand.strip(),
        model=model.strip(),
        year=year,
    )

    CarMembership.objects.create(
        car=car,
        user=telegram_account.user,
        role=MembershipRole.OWNER,
        status=MembershipStatus.ACTIVE,
        invited_by=telegram_account.user,
        joined_at=timezone.now(),
    )
    log_audit_event(
        action="car.created",
        actor=telegram_account.user,
        entity=car,
        car=car,
        context={"source": "telegram", "chat_id": chat_id},
        metadata={"plate_number": car.plate_number},
    )

    return car
