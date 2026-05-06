from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.cars.models import Car, CarMembership, MembershipRole, MembershipStatus
from apps.telegram.models import TelegramAccount
from queries.car_selector import list_cars_for_chat, list_manageable_cars_for_chat


class CarSelectorTests(TestCase):
    def test_list_cars_for_chat_returns_only_active_memberships(self) -> None:
        user = get_user_model().objects.create_user(username="driver", password="x")
        TelegramAccount.objects.create(user=user, telegram_user_id=101, chat_id=1001)

        active_car = Car.objects.create(
            plate_number="01A100AA",
            normalized_plate_number="01A100AA",
            brand="Toyota",
            model="Corolla",
            year=2020,
        )
        pending_car = Car.objects.create(
            plate_number="01A200AA",
            normalized_plate_number="01A200AA",
            brand="Toyota",
            model="Camry",
            year=2021,
        )
        revoked_car = Car.objects.create(
            plate_number="01A300AA",
            normalized_plate_number="01A300AA",
            brand="Kia",
            model="K5",
            year=2022,
        )

        CarMembership.objects.create(
            car=active_car,
            user=user,
            role=MembershipRole.OWNER,
            status=MembershipStatus.ACTIVE,
        )
        CarMembership.objects.create(
            car=pending_car,
            user=user,
            role=MembershipRole.VIEWER,
            status=MembershipStatus.PENDING,
        )
        CarMembership.objects.create(
            car=revoked_car,
            user=user,
            role=MembershipRole.MANAGER,
            status=MembershipStatus.REVOKED,
        )

        cars = list_cars_for_chat(chat_id=1001)

        self.assertEqual(cars, [active_car])

    def test_list_manageable_cars_for_chat_returns_only_owner_and_manager_roles(self) -> None:
        user = get_user_model().objects.create_user(username="manager", password="x")
        TelegramAccount.objects.create(user=user, telegram_user_id=102, chat_id=1002)

        owner_car = Car.objects.create(
            plate_number="01A101AA",
            normalized_plate_number="01A101AA",
            brand="Chevrolet",
            model="Cobalt",
            year=2019,
        )
        manager_car = Car.objects.create(
            plate_number="01A102AA",
            normalized_plate_number="01A102AA",
            brand="Chevrolet",
            model="Lacetti",
            year=2020,
        )
        viewer_car = Car.objects.create(
            plate_number="01A103AA",
            normalized_plate_number="01A103AA",
            brand="Toyota",
            model="Corolla",
            year=2021,
        )
        pending_manager_car = Car.objects.create(
            plate_number="01A104AA",
            normalized_plate_number="01A104AA",
            brand="Kia",
            model="K5",
            year=2022,
        )

        CarMembership.objects.create(
            car=owner_car,
            user=user,
            role=MembershipRole.OWNER,
            status=MembershipStatus.ACTIVE,
        )
        CarMembership.objects.create(
            car=manager_car,
            user=user,
            role=MembershipRole.MANAGER,
            status=MembershipStatus.ACTIVE,
        )
        CarMembership.objects.create(
            car=viewer_car,
            user=user,
            role=MembershipRole.VIEWER,
            status=MembershipStatus.ACTIVE,
        )
        CarMembership.objects.create(
            car=pending_manager_car,
            user=user,
            role=MembershipRole.MANAGER,
            status=MembershipStatus.PENDING,
        )

        cars = list_manageable_cars_for_chat(chat_id=1002)

        self.assertEqual(cars, [manager_car, owner_car])
