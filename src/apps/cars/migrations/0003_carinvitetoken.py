import apps.cars.models
import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cars", "0002_car_current_odometer"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="CarInviteToken",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("token", models.CharField(default=apps.cars.models.generate_invite_token, max_length=64, unique=True)),
                (
                    "role",
                    models.CharField(
                        choices=[("owner", "Owner"), ("manager", "Manager"), ("viewer", "Viewer")],
                        default="viewer",
                        max_length=16,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("active", "Active"),
                            ("accepted", "Accepted"),
                            ("revoked", "Revoked"),
                            ("expired", "Expired"),
                        ],
                        default="active",
                        max_length=16,
                    ),
                ),
                ("expires_at", models.DateTimeField()),
                ("accepted_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "accepted_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="accepted_car_invites",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "car",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="invite_tokens",
                        to="cars.car",
                    ),
                ),
                (
                    "invited_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="created_car_invites",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "car invite token",
                "verbose_name_plural": "car invite tokens",
                "db_table": "car_invite_tokens",
            },
        ),
        migrations.AddIndex(
            model_name="carinvitetoken",
            index=models.Index(fields=["token"], name="car_invite_token_idx"),
        ),
        migrations.AddIndex(
            model_name="carinvitetoken",
            index=models.Index(fields=["status", "expires_at"], name="car_invite_status_exp_idx"),
        ),
        migrations.AddIndex(
            model_name="carinvitetoken",
            index=models.Index(fields=["car", "status"], name="car_invite_car_status_idx"),
        ),
    ]
