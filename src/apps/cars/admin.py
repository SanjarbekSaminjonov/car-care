from django.contrib import admin

from apps.cars.models import Car, CarInviteToken, CarMembership


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = (
        "plate_number",
        "normalized_plate_number",
        "brand",
        "model",
        "year",
        "powertrain_type",
        "current_odometer",
        "created_at",
    )
    list_filter = ("powertrain_type", "year")
    search_fields = ("plate_number", "normalized_plate_number", "brand", "model", "vin")
    readonly_fields = ("created_at", "updated_at", "normalized_plate_number")
    ordering = ("-created_at",)


@admin.register(CarMembership)
class CarMembershipAdmin(admin.ModelAdmin):
    list_display = ("car", "user", "role", "status", "invited_by", "joined_at", "created_at")
    list_filter = ("role", "status", "created_at")
    search_fields = ("car__plate_number", "car__normalized_plate_number", "user__username")
    autocomplete_fields = ("car", "user", "invited_by")
    list_select_related = ("car", "user", "invited_by")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)


@admin.register(CarInviteToken)
class CarInviteTokenAdmin(admin.ModelAdmin):
    list_display = ("car", "role", "status", "invited_by", "accepted_by", "expires_at", "created_at")
    list_filter = ("role", "status", "created_at", "expires_at")
    search_fields = ("token", "car__plate_number", "car__normalized_plate_number")
    autocomplete_fields = ("car", "invited_by", "accepted_by")
    list_select_related = ("car", "invited_by", "accepted_by")
    readonly_fields = ("token", "accepted_at", "created_at", "updated_at")
    ordering = ("-created_at",)
