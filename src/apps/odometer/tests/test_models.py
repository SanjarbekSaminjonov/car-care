import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.cars.models import Car
from apps.odometer.models import OdometerEntry, OdometerSource


class OdometerEntryModelTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(username="driver", password="x")
        self.car = Car.objects.create(
            plate_number="01B111CD",
            normalized_plate_number="01B111CD",
            brand="Chevrolet",
            model="Cobalt",
            year=2021,
        )

    def test_creates_odometer_entry(self) -> None:
        entry = OdometerEntry.objects.create(
            car=self.car,
            value=120_500,
            entry_date=datetime.date(2026, 4, 14),
            source=OdometerSource.MANUAL,
            created_by=self.user,
        )

        self.assertEqual(entry.source, OdometerSource.MANUAL)
        self.assertEqual(entry.value, 120_500)
