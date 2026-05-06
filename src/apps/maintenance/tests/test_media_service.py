import datetime
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.audit.models import AuditEvent
from apps.cars.models import Car, CarMembership, MembershipRole, MembershipStatus
from apps.maintenance.models import MaintenanceMediaAttachment, MaintenanceMediaType, MaintenanceRecord, MaintenanceStatus
from apps.telegram.models import TelegramAccount
from policies.car_access import CarAccessDenied
from services.maintenance_media_service import TelegramMediaPayload, attach_maintenance_media_for_chat


class MaintenanceMediaServiceTests(TestCase):
    def setUp(self) -> None:
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(username="owner", password="x")
        self.viewer = user_model.objects.create_user(username="viewer", password="x")
        self.owner_account = TelegramAccount.objects.create(
            user=self.owner,
            telegram_user_id=7101,
            chat_id=8101,
        )
        self.viewer_account = TelegramAccount.objects.create(
            user=self.viewer,
            telegram_user_id=7102,
            chat_id=8102,
        )
        self.car = Car.objects.create(
            plate_number="01M123AA",
            normalized_plate_number="01M123AA",
            brand="Chevrolet",
            model="Cobalt",
            year=2020,
        )
        self.record = MaintenanceRecord.objects.create(
            car=self.car,
            event_date=datetime.date(2026, 4, 29),
            odometer=55_000,
            title="Brake service",
            total_amount=Decimal("250000"),
            created_by=self.owner,
            status=MaintenanceStatus.FINAL,
        )

    def test_owner_attaches_media_to_record(self) -> None:
        CarMembership.objects.create(
            car=self.car,
            user=self.owner,
            role=MembershipRole.OWNER,
            status=MembershipStatus.ACTIVE,
        )

        attachment = attach_maintenance_media_for_chat(
            chat_id=self.owner_account.chat_id,
            telegram_user_id=self.owner_account.telegram_user_id,
            maintenance_record_id=str(self.record.id),
            media=TelegramMediaPayload(
                media_type=MaintenanceMediaType.IMAGE,
                file_id="file-123",
                file_unique_id="unique-123",
                file_size=100,
                caption="receipt",
            ),
        )

        self.assertEqual(attachment.maintenance_record, self.record)
        self.assertEqual(attachment.telegram_file_id, "file-123")
        self.assertEqual(attachment.caption, "receipt")
        self.assertEqual(AuditEvent.objects.get().action, "maintenance.media_attached")

    def test_viewer_cannot_attach_media(self) -> None:
        CarMembership.objects.create(
            car=self.car,
            user=self.viewer,
            role=MembershipRole.VIEWER,
            status=MembershipStatus.ACTIVE,
        )

        with self.assertRaises(CarAccessDenied):
            attach_maintenance_media_for_chat(
                chat_id=self.viewer_account.chat_id,
                telegram_user_id=self.viewer_account.telegram_user_id,
                maintenance_record_id=str(self.record.id),
                media=TelegramMediaPayload(
                    media_type=MaintenanceMediaType.DOCUMENT,
                    file_id="file-456",
                    file_name="receipt.pdf",
                ),
            )

        self.assertEqual(MaintenanceMediaAttachment.objects.count(), 0)
