from django.contrib import admin

from apps.maintenance.models import MaintenanceLineItem, MaintenanceMediaAttachment, MaintenanceRecord


class MaintenanceLineItemInline(admin.TabularInline):
    model = MaintenanceLineItem
    extra = 0


class MaintenanceMediaAttachmentInline(admin.TabularInline):
    model = MaintenanceMediaAttachment
    extra = 0
    readonly_fields = ("created_at",)


@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display = ("car", "event_date", "odometer", "title", "status", "created_by", "created_at")
    list_filter = ("status", "event_date")
    search_fields = ("car__plate_number", "car__normalized_plate_number", "title", "description")
    autocomplete_fields = ("car", "created_by", "paid_by_user")
    list_select_related = ("car", "created_by", "paid_by_user")
    readonly_fields = ("created_at", "updated_at")
    inlines = (MaintenanceLineItemInline, MaintenanceMediaAttachmentInline)
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


@admin.register(MaintenanceMediaAttachment)
class MaintenanceMediaAttachmentAdmin(admin.ModelAdmin):
    list_display = ("maintenance_record", "media_type", "file_name", "mime_type", "file_size", "uploaded_by", "created_at")
    list_filter = ("media_type", "mime_type", "created_at")
    search_fields = (
        "file_name",
        "telegram_file_id",
        "telegram_file_unique_id",
        "maintenance_record__car__plate_number",
        "maintenance_record__title",
    )
    autocomplete_fields = ("maintenance_record", "uploaded_by")
    list_select_related = ("maintenance_record", "uploaded_by")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)
