from apps.cars.models import Car, CarMembership, MembershipRole, MembershipStatus

MANAGE_CAR_ROLES = (MembershipRole.OWNER, MembershipRole.MANAGER)
VIEW_CAR_ROLES = (MembershipRole.OWNER, MembershipRole.MANAGER, MembershipRole.VIEWER)
SHARE_CAR_ROLES = (MembershipRole.OWNER,)


class CarAccessDenied(PermissionError):
    """Raised when a user cannot perform the requested car action."""


def get_active_membership(*, user, car: Car) -> CarMembership | None:
    return (
        CarMembership.objects.filter(
            car=car,
            user=user,
            status=MembershipStatus.ACTIVE,
        )
        .only("id", "role", "status")
        .first()
    )


def user_can_view_car(*, user, car: Car) -> bool:
    membership = get_active_membership(user=user, car=car)
    return membership is not None and membership.role in VIEW_CAR_ROLES


def user_can_manage_car(*, user, car: Car) -> bool:
    membership = get_active_membership(user=user, car=car)
    return membership is not None and membership.role in MANAGE_CAR_ROLES


def user_can_share_car(*, user, car: Car) -> bool:
    membership = get_active_membership(user=user, car=car)
    return membership is not None and membership.role in SHARE_CAR_ROLES


def assert_user_can_view_car(*, user, car: Car) -> None:
    if not user_can_view_car(user=user, car=car):
        raise CarAccessDenied("User does not have access to this car.")


def assert_user_can_manage_car(*, user, car: Car) -> None:
    if not user_can_manage_car(user=user, car=car):
        raise CarAccessDenied("User cannot modify this car.")


def assert_user_can_share_car(*, user, car: Car) -> None:
    if not user_can_share_car(user=user, car=car):
        raise CarAccessDenied("User cannot share this car.")
