import uuid
from secrets import token_urlsafe

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


class CarInviteStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    ACCEPTED = "accepted", "Accepted"
    REVOKED = "revoked", "Revoked"
    EXPIRED = "expired", "Expired"


def generate_invite_token() -> str:
    return token_urlsafe(24)


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
    current_odometer = models.PositiveBigIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "cars"
        verbose_name = "car"
        verbose_name_plural = "cars"
        indexes = [
            models.Index(fields=["normalized_plate_number"], name="cars_normali_f4656e_idx"),
            models.Index(fields=["powertrain_type"], name="cars_powertr_353cf9_idx"),
        ]

    def save(self, *args, **kwargs):
        self.plate_number = self.plate_number.strip()
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
        indexes = [
            models.Index(fields=["status"], name="car_membersh_status_28e15b_idx"),
            models.Index(fields=["role"], name="car_membersh_role_5bb6de_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.user} -> {self.car} ({self.role})"


class CarInviteToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="invite_tokens")
    token = models.CharField(max_length=64, unique=True, default=generate_invite_token)
    role = models.CharField(
        max_length=16,
        choices=MembershipRole.choices,
        default=MembershipRole.VIEWER,
    )
    status = models.CharField(
        max_length=16,
        choices=CarInviteStatus.choices,
        default=CarInviteStatus.ACTIVE,
    )
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_car_invites",
    )
    accepted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="accepted_car_invites",
    )
    expires_at = models.DateTimeField()
    accepted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "car_invite_tokens"
        verbose_name = "car invite token"
        verbose_name_plural = "car invite tokens"
        indexes = [
            models.Index(fields=["token"], name="car_invite_token_idx"),
            models.Index(fields=["status", "expires_at"], name="car_invite_status_exp_idx"),
            models.Index(fields=["car", "status"], name="car_invite_car_status_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.car.plate_number} invite ({self.role}, {self.status})"
