import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.test import SimpleTestCase


class UserModelSmokeTests(SimpleTestCase):
    def test_custom_user_model_is_active(self) -> None:
        user_model = get_user_model()

        self.assertEqual(user_model._meta.label, "users.User")

    def test_user_primary_key_is_uuid(self) -> None:
        user_model = get_user_model()
        id_field = user_model._meta.get_field("id")

        self.assertIsInstance(id_field, models.UUIDField)
        self.assertEqual(id_field.default, uuid.uuid4)
