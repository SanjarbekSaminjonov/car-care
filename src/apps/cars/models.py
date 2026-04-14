import uuid

from django.conf import settings
from django.db import models


class CarPowertrainType(models.TextChoices):
    ICE = "ice", "ICE"
    HYBRID = "hybrid", "Hybrid"
    EV = "ev", "EV"


class MembershipRole(models.TextChoices):
    OWNER = "owner", "Owner"
    MANAGER = "manager", "Manager"
    VIEWER = "viewer", "Viewer"


class MembershipStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    PENDING = "pending", "Pending"
    REVOKED = "revoked", "Revoked"


class Car(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plate_number = models.CharField(max_length=32)
    normalized_plate_number = models.CharField(max_length=32, unique=True)
    brand = models.CharField(max_length=64)
    model = models.CharField(max_length=64)
    year = models.PositiveSmallIntegerField()
    vin = models.CharField(max_length=32, blank=True, null=True, unique=True)
    powertrain_type = models.CharField(
        max_length=16,
        choices=CarPowertrainType.choices,
        default=CarPowertrainType.ICE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "cars"
        verbose_name = "car"
        verbose_name_plural = "cars"
        indexes = [
            models.Index(fields=["normalized_plate_number"]),
            models.Index(fields=["powertrain_type"]),
        ]

    def save(self, *args, **kwargs):
        self.normalized_plate_number = self.normalize_plate(self.plate_number)
        super().save(*args, **kwargs)

    @staticmethod
    def normalize_plate(plate_number: str) -> str:
        return "".join(plate_number.upper().split())

    def __str__(self) -> str:
        return f"{self.plate_number} ({self.brand} {self.model})"


class CarMembership(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="car_memberships",
    )
    role = models.CharField(
        max_length=16,
        choices=MembershipRole.choices,
        default=MembershipRole.VIEWER,
    )
    status = models.CharField(
        max_length=16,
        choices=MembershipStatus.choices,
        default=MembershipStatus.PENDING,
    )
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sent_car_invites",
    )
    joined_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "car_memberships"
        verbose_name = "car membership"
        verbose_name_plural = "car memberships"
        constraints = [
            models.UniqueConstraint(fields=["car", "user"], name="uq_car_membership_car_user")
        ]
        indexes = [models.Index(fields=["status"]), models.Index(fields=["role"])]

    def __str__(self) -> str:
        return f"{self.user} -> {self.car} ({self.role})"
