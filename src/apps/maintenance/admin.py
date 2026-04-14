from django.contrib import admin

from apps.maintenance.models import MaintenanceLineItem, MaintenanceRecord


class MaintenanceLineItemInline(admin.TabularInline):
    model = MaintenanceLineItem
    extra = 0


@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display = ("car", "event_date", "odometer", "title", "status", "created_by", "created_at")
    list_filter = ("status", "event_date")
    search_fields = ("car__plate_number", "car__normalized_plate_number", "title", "description")
    autocomplete_fields = ("car", "created_by", "paid_by_user")
    list_select_related = ("car", "created_by", "paid_by_user")
    readonly_fields = ("created_at", "updated_at")
    inlines = (MaintenanceLineItemInline,)
    ordering = ("-event_date", "-created_at")


@admin.register(MaintenanceLineItem)
class MaintenanceLineItemAdmin(admin.ModelAdmin):
    list_display = ("maintenance_record", "item_type", "name", "quantity", "total_price", "paid_by_user")
    list_filter = ("item_type",)
    search_fields = (
        "name",
        "maintenance_record__car__plate_number",
        "maintenance_record__title",
    )
    autocomplete_fields = ("maintenance_record", "paid_by_user")
    list_select_related = ("maintenance_record", "paid_by_user")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)
