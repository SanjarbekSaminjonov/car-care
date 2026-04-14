from django.contrib import admin
from django.test import SimpleTestCase

from apps.maintenance.admin import MaintenanceLineItemAdmin, MaintenanceRecordAdmin
from apps.maintenance.models import MaintenanceLineItem, MaintenanceRecord


class MaintenanceAdminRegistrationTests(SimpleTestCase):
    def test_maintenance_models_registered(self) -> None:
        self.assertIn(MaintenanceRecord, admin.site._registry)
        self.assertIn(MaintenanceLineItem, admin.site._registry)
        self.assertIsInstance(admin.site._registry[MaintenanceRecord], MaintenanceRecordAdmin)
        self.assertIsInstance(admin.site._registry[MaintenanceLineItem], MaintenanceLineItemAdmin)
