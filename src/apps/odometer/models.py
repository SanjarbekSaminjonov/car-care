from django.conf import settings
from django.db import models

from apps.cars.models import Car


class OdometerSource(models.TextChoices):
    MANUAL = "manual", "Manual"
    MAINTENANCE_RECORD = "maintenance_record", "Maintenance Record"
    OCR = "ocr", "OCR"
    SYSTEM = "system", "System"


class OdometerEntry(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="odometer_entries")
    value = models.PositiveBigIntegerField()
    entry_date = models.DateField()
    source = models.CharField(max_length=32, choices=OdometerSource.choices)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_odometer_entries",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "odometer_entries"
        verbose_name = "odometer entry"
        verbose_name_plural = "odometer entries"
        indexes = [models.Index(fields=["car", "entry_date"]), models.Index(fields=["source"])]

    def __str__(self) -> str:
        return f"{self.car.plate_number}: {self.value} km"
