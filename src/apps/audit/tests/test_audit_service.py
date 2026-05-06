from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.audit.models import AuditActorType, AuditEvent
from apps.cars.models import Car
from services.audit_service import log_audit_event


class AuditServiceTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(username="owner", password="secret12345")
        self.car = Car.objects.create(
            plate_number="01A777BC",
            normalized_plate_number="01A777BC",
            brand="Toyota",
            model="Camry",
            year=2022,
        )

    def test_log_event_derives_entity_identity(self) -> None:
        event = log_audit_event(
            action="car.created",
            actor=self.user,
            entity=self.car,
            car=self.car,
            context={"source": "test"},
            metadata={"plate": self.car.plate_number},
        )

        self.assertEqual(event.actor, self.user)
        self.assertEqual(event.actor_type, AuditActorType.USER)
        self.assertEqual(event.entity_type, "cars.car")
        self.assertEqual(event.entity_id, str(self.car.id))
        self.assertEqual(event.car, self.car)
        self.assertEqual(event.context, {"source": "test"})
        self.assertEqual(event.metadata, {"plate": "01A777BC"})

    def test_log_system_event_without_actor(self) -> None:
        event = log_audit_event(
            action="worker.started",
            entity_type="notifications.worker",
            entity_id="due-notifications",
        )

        self.assertIsNone(event.actor)
        self.assertEqual(event.actor_type, AuditActorType.SYSTEM)
        self.assertEqual(event.entity_type, "notifications.worker")
        self.assertEqual(event.entity_id, "due-notifications")

    def test_rejects_blank_action(self) -> None:
        with self.assertRaises(ValidationError):
            log_audit_event(action=" ")

        self.assertEqual(AuditEvent.objects.count(), 0)
