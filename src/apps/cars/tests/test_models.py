from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from apps.cars.models import Car, CarMembership, MembershipRole, MembershipStatus


class CarModelTests(TestCase):
    def test_plate_is_normalized_on_save(self) -> None:
        car = Car.objects.create(
            plate_number=" 01 a 123 bc ",
            normalized_plate_number="ignored",
            brand="Toyota",
            model="Corolla",
            year=2022,
        )

        self.assertEqual(car.normalized_plate_number, "01A123BC")

    def test_vin_must_be_unique_when_present(self) -> None:
        Car.objects.create(
            plate_number="01A123BC",
            normalized_plate_number="01A123BC",
            brand="Toyota",
            model="Corolla",
            year=2020,
            vin="VIN-1",
        )

        with self.assertRaises(IntegrityError):
            Car.objects.create(
                plate_number="01A124BC",
                normalized_plate_number="01A124BC",
                brand="Honda",
                model="Civic",
                year=2021,
                vin="VIN-1",
            )


class CarMembershipModelTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(username="owner", password="x")
        self.car = Car.objects.create(
            plate_number="01A555BC",
            normalized_plate_number="01A555BC",
            brand="Kia",
            model="K5",
            year=2023,
        )

    def test_membership_is_unique_per_car_and_user(self) -> None:
        CarMembership.objects.create(
            car=self.car,
            user=self.user,
            role=MembershipRole.OWNER,
            status=MembershipStatus.ACTIVE,
        )

        with self.assertRaises(IntegrityError):
            CarMembership.objects.create(
                car=self.car,
                user=self.user,
                role=MembershipRole.VIEWER,
                status=MembershipStatus.PENDING,
            )
