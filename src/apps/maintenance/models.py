import uuid

from django.conf import settings
from django.db import models

from apps.cars.models import Car


class MaintenanceStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    FINAL = "final", "Final"


class MaintenanceItemType(models.TextChoices):
    PART = "part", "Part"
    LABOR = "labor", "Labor"
    SERVICE = "service", "Service"
    FEE = "fee", "Fee"
    FLUID = "fluid", "Fluid"
    FILTER = "filter", "Filter"
    OTHER = "other", "Other"


class MaintenanceMediaType(models.TextChoices):
    IMAGE = "image", "Image"
    VIDEO = "video", "Video"
    DOCUMENT = "document", "Document"
    AUDIO = "audio", "Audio"


class MaintenanceRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="maintenance_records")
    event_date = models.DateField()
    odometer = models.PositiveBigIntegerField()
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_maintenance_records",
    )
    paid_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="paid_maintenance_records",
    )
    paid_by_label = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=16, choices=MaintenanceStatus.choices, default=MaintenanceStatus.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "maintenance_records"
        verbose_name = "maintenance record"
        verbose_name_plural = "maintenance records"
        indexes = [
            models.Index(fields=["car", "event_date"], name="maintenanc_car_id_ffd987_idx"),
            models.Index(fields=["status"], name="maintenanc_status_206c4b_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.car.plate_number} - {self.title}"


class MaintenanceLineItem(models.Model):
    maintenance_record = models.ForeignKey(
        MaintenanceRecord,
        on_delete=models.CASCADE,
        related_name="line_items",
    )
    item_type = models.CharField(max_length=16, choices=MaintenanceItemType.choices)
    name = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=14, decimal_places=2)
    total_price = models.DecimalField(max_digits=14, decimal_places=2)
    paid_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="paid_maintenance_line_items",
    )
    paid_by_label = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "maintenance_line_items"
        verbose_name = "maintenance line item"
        verbose_name_plural = "maintenance line items"
        indexes = [models.Index(fields=["item_type"], name="maintenanc_item_ty_16945b_idx")]

    def __str__(self) -> str:
        return f"{self.name} ({self.item_type})"


class MaintenanceMediaAttachment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    maintenance_record = models.ForeignKey(
        MaintenanceRecord,
        on_delete=models.CASCADE,
        related_name="media_attachments",
    )
    media_type = models.CharField(max_length=16, choices=MaintenanceMediaType.choices)
    telegram_file_id = models.CharField(max_length=512)
    telegram_file_unique_id = models.CharField(max_length=255, blank=True)
    file_name = models.CharField(max_length=255, blank=True)
    mime_type = models.CharField(max_length=255, blank=True)
    file_size = models.PositiveBigIntegerField(null=True, blank=True)
    caption = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_maintenance_media",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "maintenance_media_attachments"
        verbose_name = "maintenance media attachment"
        verbose_name_plural = "maintenance media attachments"
        indexes = [
            models.Index(fields=["maintenance_record", "created_at"], name="maint_media_record_time_idx"),
            models.Index(fields=["media_type"], name="maint_media_type_idx"),
        ]

    def __str__(self) -> str:
        label = self.file_name or self.media_type
        return f"{self.maintenance_record_id} - {label}"
