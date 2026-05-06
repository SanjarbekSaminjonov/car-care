from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.audit.models import AuditEvent
from apps.cars.models import Car, CarMembership, MembershipRole, MembershipStatus
from apps.odometer.models import OdometerEntry
from apps.telegram.models import TelegramAccount
from policies.car_access import CarAccessDenied
from services.odometer_service import create_odometer_for_chat


class OdometerServiceTests(TestCase):
    def setUp(self) -> None:
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(username="owner", password="x")
        self.viewer = user_model.objects.create_user(username="viewer", password="x")
        self.owner_account = TelegramAccount.objects.create(
            user=self.owner,
            telegram_user_id=100,
            chat_id=1000,
        )
        self.viewer_account = TelegramAccount.objects.create(
            user=self.viewer,
            telegram_user_id=200,
            chat_id=2000,
        )
        self.car = Car.objects.create(
            plate_number="01A123BC",
            normalized_plate_number="01A123BC",
            brand="Chevrolet",
            model="Cobalt",
            year=2021,
        )

    def test_create_odometer_updates_car_current_odometer(self) -> None:
        CarMembership.objects.create(
            car=self.car,
            user=self.owner,
            role=MembershipRole.OWNER,
            status=MembershipStatus.ACTIVE,
        )

        entry = create_odometer_for_chat(
            chat_id=self.owner_account.chat_id,
            telegram_user_id=self.owner_account.telegram_user_id,
            plate_number="01 a 123 bc",
            value=120_500,
        )

        self.car.refresh_from_db()
        self.assertEqual(entry.value, 120_500)
        self.assertEqual(self.car.current_odometer, 120_500)
        self.assertEqual(AuditEvent.objects.get().action, "odometer.recorded")

    def test_rejects_lower_odometer_without_partial_write(self) -> None:
        self.car.current_odometer = 120_500
        self.car.save(update_fields=["current_odometer", "updated_at"])
        CarMembership.objects.create(
            car=self.car,
            user=self.owner,
            role=MembershipRole.MANAGER,
            status=MembershipStatus.ACTIVE,
        )

        with self.assertRaises(ValidationError):
            create_odometer_for_chat(
                chat_id=self.owner_account.chat_id,
                telegram_user_id=self.owner_account.telegram_user_id,
                plate_number="01A123BC",
                value=119_000,
            )

        self.assertEqual(OdometerEntry.objects.count(), 0)

    def test_viewer_cannot_update_odometer(self) -> None:
        CarMembership.objects.create(
            car=self.car,
            user=self.viewer,
            role=MembershipRole.VIEWER,
            status=MembershipStatus.ACTIVE,
        )

        with self.assertRaises(CarAccessDenied):
            create_odometer_for_chat(
                chat_id=self.viewer_account.chat_id,
                telegram_user_id=self.viewer_account.telegram_user_id,
                plate_number="01A123BC",
                value=10_000,
            )
