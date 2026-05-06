from django.contrib import admin

from apps.audit.models import AuditEvent


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ("action", "entity_type", "entity_id", "actor", "actor_type", "car", "occurred_at")
    list_filter = ("actor_type", "action", "occurred_at")
    search_fields = ("action", "entity_type", "entity_id", "actor__username", "car__plate_number")
    autocomplete_fields = ("actor", "car")
    list_select_related = ("actor", "car")
    readonly_fields = (
        "id",
        "actor",
        "actor_type",
        "action",
        "entity_type",
        "entity_id",
        "car",
        "context",
        "metadata",
        "occurred_at",
    )
    ordering = ("-occurred_at",)

    def has_add_permission(self, request) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False
