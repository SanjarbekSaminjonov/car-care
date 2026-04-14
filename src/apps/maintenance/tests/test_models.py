import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.cars.models import Car
from apps.maintenance.models import (
    MaintenanceItemType,
    MaintenanceLineItem,
    MaintenanceRecord,
    MaintenanceStatus,
)


class MaintenanceModelTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(username="mechanic", password="x")
        self.car = Car.objects.create(
            plate_number="01C222DD",
            normalized_plate_number="01C222DD",
            brand="Hyundai",
            model="Elantra",
            year=2024,
        )

    def test_record_and_line_item_relation(self) -> None:
        record = MaintenanceRecord.objects.create(
            car=self.car,
            event_date=datetime.date(2026, 4, 14),
            odometer=50_000,
            title="Oil change",
            description="Engine oil + filter",
            created_by=self.user,
            status=MaintenanceStatus.FINAL,
        )

        item = MaintenanceLineItem.objects.create(
            maintenance_record=record,
            item_type=MaintenanceItemType.FLUID,
            name="5W-30 oil",
            quantity=4,
            unit_price=12.5,
            total_price=50,
            paid_by_user=self.user,
        )

        self.assertEqual(record.line_items.count(), 1)
        self.assertEqual(record.line_items.first(), item)
