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


class MaintenanceRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="maintenance_records")
    event_date = models.DateField()
    odometer = models.PositiveBigIntegerField()
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
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
    status = models.CharField(max_length=16, choices=MaintenanceStatus.choices, default=MaintenanceStatus.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "maintenance_records"
        verbose_name = "maintenance record"
        verbose_name_plural = "maintenance records"
        indexes = [models.Index(fields=["car", "event_date"]), models.Index(fields=["status"])]

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
        indexes = [models.Index(fields=["item_type"])]

    def __str__(self) -> str:
        return f"{self.name} ({self.item_type})"
