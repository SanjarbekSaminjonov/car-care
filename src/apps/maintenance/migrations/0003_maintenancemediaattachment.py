import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("maintenance", "0002_record_payment_totals"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="MaintenanceMediaAttachment",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                (
                    "media_type",
                    models.CharField(
                        choices=[
                            ("image", "Image"),
                            ("video", "Video"),
                            ("document", "Document"),
                            ("audio", "Audio"),
                        ],
                        max_length=16,
                    ),
                ),
                ("telegram_file_id", models.CharField(max_length=512)),
                ("telegram_file_unique_id", models.CharField(blank=True, max_length=255)),
                ("file_name", models.CharField(blank=True, max_length=255)),
                ("mime_type", models.CharField(blank=True, max_length=255)),
                ("file_size", models.PositiveBigIntegerField(blank=True, null=True)),
                ("caption", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "maintenance_record",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="media_attachments",
                        to="maintenance.maintenancerecord",
                    ),
                ),
                (
                    "uploaded_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="uploaded_maintenance_media",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "maintenance media attachment",
                "verbose_name_plural": "maintenance media attachments",
                "db_table": "maintenance_media_attachments",
            },
        ),
        migrations.AddIndex(
            model_name="maintenancemediaattachment",
            index=models.Index(fields=["maintenance_record", "created_at"], name="maint_media_record_time_idx"),
        ),
        migrations.AddIndex(
            model_name="maintenancemediaattachment",
            index=models.Index(fields=["media_type"], name="maint_media_type_idx"),
        ),
    ]
