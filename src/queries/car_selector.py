from apps.cars.models import Car, MembershipRole, MembershipStatus
from apps.telegram.models import TelegramAccount


def list_cars_for_chat(*, chat_id: int) -> list[Car]:
    telegram_account = (
        TelegramAccount.objects.only("user_id").filter(chat_id=chat_id).first()
    )
    if telegram_account is None:
        return []

    return list(
        Car.objects.filter(
            memberships__user_id=telegram_account.user_id,
            memberships__status=MembershipStatus.ACTIVE,
        )
        .distinct()
        .order_by("-created_at")
    )


def get_active_car_for_user_by_plate(*, user_id, plate_number: str) -> Car:
    normalized_plate = Car.normalize_plate(plate_number)
    return Car.objects.get(
        normalized_plate_number=normalized_plate,
        memberships__user_id=user_id,
        memberships__status=MembershipStatus.ACTIVE,
    )


def list_manageable_cars_for_chat(*, chat_id: int) -> list[Car]:
    telegram_account = (
        TelegramAccount.objects.only("user_id").filter(chat_id=chat_id).first()
    )
    if telegram_account is None:
        return []

    return list(
        Car.objects.filter(
            memberships__user_id=telegram_account.user_id,
            memberships__status=MembershipStatus.ACTIVE,
            memberships__role__in=(MembershipRole.OWNER, MembershipRole.MANAGER),
        )
        .distinct()
        .order_by("-created_at")
    )
