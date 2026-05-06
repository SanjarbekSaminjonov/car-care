import datetime
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.cars.models import Car, CarMembership, MembershipRole, MembershipStatus
from apps.maintenance.models import (
    MaintenanceItemType,
    MaintenanceLineItem,
    MaintenanceRecord,
    MaintenanceStatus,
)
from apps.telegram.models import TelegramAccount
from bot.formatters.messages import format_maintenance_history
from queries.maintenance_history import list_maintenance_history_for_chat


class MaintenanceHistoryTests(TestCase):
    def test_lists_history_for_active_member_and_formats_summary(self) -> None:
        user = get_user_model().objects.create_user(username="driver", password="x")
        TelegramAccount.objects.create(user=user, telegram_user_id=901, chat_id=1901)
        car = Car.objects.create(
            plate_number="01H123AA",
            normalized_plate_number="01H123AA",
            brand="Kia",
            model="K5",
            year=2022,
        )
        CarMembership.objects.create(
            car=car,
            user=user,
            role=MembershipRole.VIEWER,
            status=MembershipStatus.ACTIVE,
        )
        record = MaintenanceRecord.objects.create(
            car=car,
            event_date=datetime.date(2026, 4, 29),
            odometer=42_000,
            title="Oil change",
            total_amount=Decimal("350000"),
            created_by=user,
            status=MaintenanceStatus.FINAL,
        )
        MaintenanceLineItem.objects.create(
            maintenance_record=record,
            item_type=MaintenanceItemType.FLUID,
            name="Engine oil",
            quantity=1,
            unit_price=Decimal("350000"),
            total_price=Decimal("350000"),
        )

        records = list_maintenance_history_for_chat(chat_id=1901, plate_number="01H123AA")
        rendered = format_maintenance_history(records)

        self.assertEqual(records, [record])
        self.assertIn("Servis tarixi", rendered)
        self.assertIn("Oil change", rendered)
        self.assertIn("350 000", rendered)
        self.assertIn("Engine oil", rendered)
