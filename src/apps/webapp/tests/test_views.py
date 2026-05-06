import json
from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.cars.models import Car, CarMembership, MembershipRole, MembershipStatus
from apps.maintenance.models import MaintenanceRecord
from apps.telegram.models import TelegramAccount
from apps.webapp.tests.test_auth import signed_init_data


class WebAppViewTests(TestCase):
    def setUp(self) -> None:
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username="driver", password="x")
        self.account = TelegramAccount.objects.create(
            user=self.user,
            telegram_user_id=1001,
            chat_id=1001,
        )
        self.car = Car.objects.create(
            plate_number="40B413YA",
            normalized_plate_number="40B413YA",
            brand="Chevrolet",
            model="Cobalt",
            year=2015,
            current_odometer=120_000,
        )
        CarMembership.objects.create(
            car=self.car,
            user=self.user,
            role=MembershipRole.OWNER,
            status=MembershipStatus.ACTIVE,
        )

    @override_settings(TELEGRAM_BOT_TOKEN="token-123", TELEGRAM_WEBAPP_AUTH_MAX_AGE_SECONDS=86400)
    def test_telegram_auth_logs_user_in(self) -> None:
        response = self.client.post(
            reverse("webapp:telegram_auth"),
            data=json.dumps({"init_data": signed_init_data(user_id=1001)}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertEqual(self.client.session["_auth_user_id"], str(self.user.pk))

    def test_dashboard_renders_cars(self) -> None:
        self.client.force_login(self.user)

        response = self.client.get(reverse("webapp:dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "40B413YA")
        self.assertContains(response, "Chevrolet Cobalt")

    def test_create_maintenance_from_webapp(self) -> None:
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("webapp:maintenance_create"),
            data={
                "car_id": str(self.car.id),
                "title": "Oil change",
                "event_date": "2026-04-20",
                "odometer": "119000",
                "item_name": "Engine oil",
                "item_amount": "350000",
            },
        )

        self.assertRedirects(response, reverse("webapp:dashboard"))
        record = MaintenanceRecord.objects.get()
        self.assertEqual(record.event_date, date(2026, 4, 20))
        self.assertEqual(record.total_amount, Decimal("350000"))
        self.car.refresh_from_db()
        self.assertEqual(self.car.current_odometer, 120_000)
