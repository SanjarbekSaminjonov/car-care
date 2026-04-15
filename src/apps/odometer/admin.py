from django.contrib import admin

from apps.odometer.models import OdometerEntry


@admin.register(OdometerEntry)
class OdometerEntryAdmin(admin.ModelAdmin):
    list_display = ("car", "value", "entry_date", "source", "created_by", "created_at")
    list_filter = ("source", "entry_date")
    search_fields = ("car__plate_number", "car__normalized_plate_number", "created_by__username")
    autocomplete_fields = ("car", "created_by")
    list_select_related = ("car", "created_by")
    readonly_fields = ("created_at",)
    ordering = ("-entry_date", "-created_at")
