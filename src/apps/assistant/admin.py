from django.contrib import admin

from apps.assistant.models import AssistantInteraction


@admin.register(AssistantInteraction)
class AssistantInteractionAdmin(admin.ModelAdmin):
    list_display = (
        "chat_id",
        "user",
        "provider",
        "model_name",
        "status",
        "created_at",
        "completed_at",
    )
    list_filter = ("status", "provider", "model_name", "created_at")
    search_fields = ("=chat_id", "question", "answer", "error_message", "user__username")
    readonly_fields = (
        "id",
        "telegram_account",
        "user",
        "chat_id",
        "question",
        "answer",
        "provider",
        "model_name",
        "status",
        "car_context",
        "response_metadata",
        "error_message",
        "created_at",
        "completed_at",
    )
    list_select_related = ("telegram_account", "user")
    ordering = ("-created_at",)
