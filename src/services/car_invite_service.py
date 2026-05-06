from dataclasses import dataclass
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.cars.models import (
    CarInviteStatus,
    CarInviteToken,
    CarMembership,
    MembershipRole,
    MembershipStatus,
)
from policies.car_access import assert_user_can_share_car
from queries.car_selector import get_active_car_for_user_by_plate
from services.audit_service import log_audit_event
from services.telegram_account_service import get_telegram_account_for_chat

ROLE_RANK = {
    MembershipRole.VIEWER: 1,
    MembershipRole.MANAGER: 2,
    MembershipRole.OWNER: 3,
}


class CarInviteError(ValidationError):
    """Raised when a car invite cannot be created or accepted."""


@dataclass(frozen=True)
class AcceptedCarInvite:
    invite: CarInviteToken
    membership: CarMembership
    was_created: bool


def _normalize_invite_role(role: str) -> str:
    role = role.strip().lower()
    if role not in {MembershipRole.VIEWER, MembershipRole.MANAGER}:
        raise CarInviteError("Invite role must be viewer or manager.")
    return role


@transaction.atomic
def create_car_invite_for_chat(
    *,
    chat_id: int,
    telegram_user_id: int,
    plate_number: str,
    role: str = MembershipRole.VIEWER,
    expires_in_days: int = 7,
) -> CarInviteToken:
    if expires_in_days <= 0:
        raise CarInviteError("Invite expiry must be positive.")

    telegram_account = get_telegram_account_for_chat(
        chat_id=chat_id,
        telegram_user_id=telegram_user_id,
    )
    car = get_active_car_for_user_by_plate(
        user_id=telegram_account.user_id,
        plate_number=plate_number,
    )
    assert_user_can_share_car(user=telegram_account.user, car=car)

    invite = CarInviteToken.objects.create(
        car=car,
        role=_normalize_invite_role(role),
        invited_by=telegram_account.user,
        expires_at=timezone.now() + timedelta(days=expires_in_days),
    )
    log_audit_event(
        action="car.invite_created",
        actor=telegram_account.user,
        entity=invite,
        car=car,
        context={"source": "telegram", "chat_id": chat_id},
        metadata={"role": invite.role, "expires_at": invite.expires_at.isoformat()},
    )
    return invite


def _resolve_membership_role(*, current_role: str | None, invite_role: str) -> str:
    if current_role is None:
        return invite_role
    if ROLE_RANK.get(current_role, 0) >= ROLE_RANK.get(invite_role, 0):
        return current_role
    return invite_role


def accept_car_invite_for_chat(
    *,
    chat_id: int,
    telegram_user_id: int,
    token: str,
) -> AcceptedCarInvite:
    token = token.strip()
    if not token:
        raise CarInviteError("Invite token is required.")

    telegram_account = get_telegram_account_for_chat(
        chat_id=chat_id,
        telegram_user_id=telegram_user_id,
    )

    with transaction.atomic():
        invite = CarInviteToken.objects.select_for_update().select_related("car").get(
            token=token
        )

        now = timezone.now()
        if invite.status != CarInviteStatus.ACTIVE:
            raise CarInviteError("Invite is not active.")
        if invite.expires_at <= now:
            invite.status = CarInviteStatus.EXPIRED
            invite.save(update_fields=["status", "updated_at"])
            expired = True
        else:
            expired = False

        if not expired:
            membership = (
                CarMembership.objects.select_for_update()
                .filter(car=invite.car, user=telegram_account.user)
                .first()
            )
            was_created = membership is None
            if membership is None:
                membership = CarMembership(
                    car=invite.car,
                    user=telegram_account.user,
                    invited_by=invite.invited_by,
                )

            membership.role = _resolve_membership_role(
                current_role=membership.role if membership.pk else None,
                invite_role=invite.role,
            )
            membership.status = MembershipStatus.ACTIVE
            membership.joined_at = membership.joined_at or now
            membership.invited_by = membership.invited_by or invite.invited_by
            membership.save()

            invite.status = CarInviteStatus.ACCEPTED
            invite.accepted_by = telegram_account.user
            invite.accepted_at = now
            invite.save(update_fields=["status", "accepted_by", "accepted_at", "updated_at"])

            log_audit_event(
                action="car.invite_accepted",
                actor=telegram_account.user,
                entity=invite,
                car=invite.car,
                context={"source": "telegram", "chat_id": chat_id},
                metadata={"role": membership.role, "membership_created": was_created},
            )

            return AcceptedCarInvite(
                invite=invite,
                membership=membership,
                was_created=was_created,
            )

    raise CarInviteError("Invite has expired.")
