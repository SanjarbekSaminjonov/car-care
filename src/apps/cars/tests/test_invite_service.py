from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from apps.cars.models import (
    Car,
    CarInviteStatus,
    CarInviteToken,
    CarMembership,
    MembershipRole,
    MembershipStatus,
)
from apps.telegram.models import TelegramAccount
from policies.car_access import CarAccessDenied
from services.car_invite_service import accept_car_invite_for_chat, create_car_invite_for_chat


class CarInviteServiceTests(TestCase):
    def setUp(self) -> None:
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(username="owner", password="x")
        self.viewer = user_model.objects.create_user(username="viewer", password="x")
        self.new_user = user_model.objects.create_user(username="new-user", password="x")
        self.owner_account = TelegramAccount.objects.create(
            user=self.owner,
            telegram_user_id=1001,
            chat_id=2001,
        )
        self.viewer_account = TelegramAccount.objects.create(
            user=self.viewer,
            telegram_user_id=1002,
            chat_id=2002,
        )
        self.new_account = TelegramAccount.objects.create(
            user=self.new_user,
            telegram_user_id=1003,
            chat_id=2003,
        )
        self.car = Car.objects.create(
            plate_number="01S777AA",
            normalized_plate_number="01S777AA",
            brand="Toyota",
            model="Corolla",
            year=2021,
        )
        CarMembership.objects.create(
            car=self.car,
            user=self.owner,
            role=MembershipRole.OWNER,
            status=MembershipStatus.ACTIVE,
        )

    def test_owner_creates_invite_and_user_accepts(self) -> None:
        invite = create_car_invite_for_chat(
            chat_id=self.owner_account.chat_id,
            telegram_user_id=self.owner_account.telegram_user_id,
            plate_number="01S777AA",
            role=MembershipRole.MANAGER,
        )

        result = accept_car_invite_for_chat(
            chat_id=self.new_account.chat_id,
            telegram_user_id=self.new_account.telegram_user_id,
            token=invite.token,
        )

        invite.refresh_from_db()
        self.assertEqual(invite.status, CarInviteStatus.ACCEPTED)
        self.assertEqual(result.membership.user, self.new_user)
        self.assertEqual(result.membership.role, MembershipRole.MANAGER)
        self.assertEqual(result.membership.status, MembershipStatus.ACTIVE)

    def test_viewer_cannot_create_invite(self) -> None:
        CarMembership.objects.create(
            car=self.car,
            user=self.viewer,
            role=MembershipRole.VIEWER,
            status=MembershipStatus.ACTIVE,
        )

        with self.assertRaises(CarAccessDenied):
            create_car_invite_for_chat(
                chat_id=self.viewer_account.chat_id,
                telegram_user_id=self.viewer_account.telegram_user_id,
                plate_number="01S777AA",
                role=MembershipRole.VIEWER,
            )

    def test_accept_expired_invite_marks_expired(self) -> None:
        invite = CarInviteToken.objects.create(
            car=self.car,
            role=MembershipRole.VIEWER,
            invited_by=self.owner,
            expires_at=timezone.now() - timedelta(minutes=1),
        )

        with self.assertRaises(ValidationError):
            accept_car_invite_for_chat(
                chat_id=self.new_account.chat_id,
                telegram_user_id=self.new_account.telegram_user_id,
                token=invite.token,
            )

        invite.refresh_from_db()
        self.assertEqual(invite.status, CarInviteStatus.EXPIRED)
