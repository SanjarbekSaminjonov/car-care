from django.contrib import admin
from django.test import SimpleTestCase

from apps.cars.admin import CarAdmin, CarMembershipAdmin
from apps.cars.models import Car, CarMembership


class CarAdminRegistrationTests(SimpleTestCase):
    def test_cars_are_registered_in_admin(self) -> None:
        self.assertIn(Car, admin.site._registry)
        self.assertIn(CarMembership, admin.site._registry)
        self.assertIsInstance(admin.site._registry[Car], CarAdmin)
        self.assertIsInstance(admin.site._registry[CarMembership], CarMembershipAdmin)
