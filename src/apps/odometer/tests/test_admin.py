from django.contrib import admin
from django.test import SimpleTestCase

from apps.odometer.admin import OdometerEntryAdmin
from apps.odometer.models import OdometerEntry


class OdometerAdminRegistrationTests(SimpleTestCase):
    def test_odometer_is_registered_in_admin(self) -> None:
        self.assertIn(OdometerEntry, admin.site._registry)
        self.assertIsInstance(admin.site._registry[OdometerEntry], OdometerEntryAdmin)
