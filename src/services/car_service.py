from django.db import transaction

from apps.cars.models import Car, CarMembership, MembershipRole, MembershipStatus
from apps.telegram.models import TelegramAccount


@transaction.atomic
def create_car_for_chat(
    *, chat_id: int, plate_number: str, brand: str, model: str, year: int
) -> Car:
    telegram_account = TelegramAccount.objects.select_related("user").get(chat_id=chat_id)

    car = Car.objects.create(
        plate_number=plate_number,
        normalized_plate_number=plate_number,
        brand=brand,
        model=model,
        year=year,
    )

    CarMembership.objects.create(
        car=car,
        user=telegram_account.user,
        role=MembershipRole.OWNER,
        status=MembershipStatus.ACTIVE,
        invited_by=telegram_account.user,
    )

    return car
