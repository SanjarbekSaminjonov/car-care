from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from apps.audit.models import AuditEvent
from apps.cars.models import Car, CarMembership, MembershipRole, MembershipStatus
from apps.maintenance.models import MaintenanceLineItem, MaintenanceRecord
from apps.odometer.models import OdometerEntry, OdometerSource
from apps.telegram.models import TelegramAccount
from policies.car_access import CarAccessDenied
from services.maintenance_service import create_maintenance_for_chat


class MaintenanceServiceTests(TestCase):
    def setUp(self) -> None:
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(username="owner", password="x")
        self.viewer = user_model.objects.create_user(username="viewer", password="x")
        self.owner_account = TelegramAccount.objects.create(
            user=self.owner,
            telegram_user_id=501,
            chat_id=5001,
        )
        self.viewer_account = TelegramAccount.objects.create(
            user=self.viewer,
            telegram_user_id=502,
            chat_id=5002,
        )
        self.car = Car.objects.create(
            plate_number="01B777CC",
            normalized_plate_number="01B777CC",
            brand="Hyundai",
            model="Elantra",
            year=2023,
        )

    def test_create_maintenance_creates_line_item_and_odometer_entry(self) -> None:
        CarMembership.objects.create(
            car=self.car,
            user=self.owner,
            role=MembershipRole.OWNER,
            status=MembershipStatus.ACTIVE,
        )

        record = create_maintenance_for_chat(
            chat_id=self.owner_account.chat_id,
            telegram_user_id=self.owner_account.telegram_user_id,
            plate_number="01B777CC",
            title="Oil change",
            event_date=date(2026, 4, 20),
            odometer=50_000,
            item_name="Engine oil",
            item_amount=Decimal("350000"),
        )

        self.car.refresh_from_db()
        line_item = MaintenanceLineItem.objects.get(maintenance_record=record)
        odometer_entry = OdometerEntry.objects.get(maintenance_record=record)

        self.assertEqual(record.total_amount, Decimal("350000"))
        self.assertEqual(record.event_date, date(2026, 4, 20))
        self.assertEqual(line_item.total_price, Decimal("350000"))
        self.assertEqual(odometer_entry.source, OdometerSource.MAINTENANCE_RECORD)
        self.assertEqual(odometer_entry.entry_date, date(2026, 4, 20))
        self.assertEqual(self.car.current_odometer, 50_000)
        self.assertEqual(
            set(AuditEvent.objects.values_list("action", flat=True)),
            {"maintenance.created", "odometer.recorded"},
        )

    def test_viewer_cannot_create_maintenance(self) -> None:
        CarMembership.objects.create(
            car=self.car,
            user=self.viewer,
            role=MembershipRole.VIEWER,
            status=MembershipStatus.ACTIVE,
        )

        with self.assertRaises(CarAccessDenied):
            create_maintenance_for_chat(
                chat_id=self.viewer_account.chat_id,
                telegram_user_id=self.viewer_account.telegram_user_id,
                plate_number="01B777CC",
                title="Oil change",
                event_date=date(2026, 4, 20),
                odometer=50_000,
                item_name="Engine oil",
                item_amount=Decimal("350000"),
            )

    def test_historical_maintenance_allows_lower_odometer_without_lowering_current(self) -> None:
        self.car.current_odometer = 60_000
        self.car.save(update_fields=["current_odometer", "updated_at"])
        CarMembership.objects.create(
            car=self.car,
            user=self.owner,
            role=MembershipRole.OWNER,
            status=MembershipStatus.ACTIVE,
        )

        record = create_maintenance_for_chat(
            chat_id=self.owner_account.chat_id,
            telegram_user_id=self.owner_account.telegram_user_id,
            plate_number="01B777CC",
            title="Oil change",
            event_date=date(2026, 4, 20),
            odometer=50_000,
            item_name="Engine oil",
            item_amount=Decimal("350000"),
        )

        self.car.refresh_from_db()
        self.assertEqual(record.odometer, 50_000)
        self.assertEqual(MaintenanceRecord.objects.count(), 1)
        self.assertEqual(MaintenanceLineItem.objects.count(), 1)
        self.assertEqual(OdometerEntry.objects.get(maintenance_record=record).value, 50_000)
        self.assertEqual(self.car.current_odometer, 60_000)
        self.assertEqual(
            set(AuditEvent.objects.values_list("action", flat=True)),
            {"maintenance.created", "odometer.recorded"},
        )

    def test_future_event_date_is_rejected_without_partial_write(self) -> None:
        CarMembership.objects.create(
            car=self.car,
            user=self.owner,
            role=MembershipRole.OWNER,
            status=MembershipStatus.ACTIVE,
        )

        with self.assertRaises(ValidationError):
            create_maintenance_for_chat(
                chat_id=self.owner_account.chat_id,
                telegram_user_id=self.owner_account.telegram_user_id,
                plate_number="01B777CC",
                title="Oil change",
                event_date=timezone.localdate() + timedelta(days=1),
                odometer=50_000,
                item_name="Engine oil",
                item_amount=Decimal("350000"),
            )

        self.assertEqual(MaintenanceRecord.objects.count(), 0)
        self.assertEqual(MaintenanceLineItem.objects.count(), 0)
        self.assertEqual(OdometerEntry.objects.count(), 0)
