from django.contrib import admin

from apps.telegram.models import BotConversationState, ProcessedTelegramUpdate, TelegramAccount


@admin.register(TelegramAccount)
class TelegramAccountAdmin(admin.ModelAdmin):
    list_display = (
        "telegram_user_id",
        "user",
        "chat_id",
        "username",
        "is_blocked",
        "last_seen_at",
        "created_at",
    )
    list_filter = ("is_blocked", "language_code", "created_at")
    search_fields = (
        "=telegram_user_id",
        "=chat_id",
        "username",
        "first_name",
        "last_name",
        "user__username",
        "user__email",
    )
    readonly_fields = ("created_at", "updated_at", "last_seen_at")
    list_select_related = ("user",)
    autocomplete_fields = ("user",)
    ordering = ("-created_at",)


@admin.register(BotConversationState)
class BotConversationStateAdmin(admin.ModelAdmin):
    list_display = ("chat_id", "flow_name", "state_name", "expires_at", "updated_at")
    list_filter = ("flow_name", "state_name")
    search_fields = ("=chat_id", "flow_name", "state_name")
    autocomplete_fields = ("telegram_account",)
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-updated_at",)


@admin.register(ProcessedTelegramUpdate)
class ProcessedTelegramUpdateAdmin(admin.ModelAdmin):
    list_display = (
        "update_id",
        "status",
        "update_type",
        "chat_id",
        "telegram_user_id",
        "processed_at",
    )
    list_filter = ("status", "update_type", "processed_at")
    search_fields = ("=update_id", "=chat_id", "=telegram_user_id")
    readonly_fields = (
        "update_id",
        "chat_id",
        "telegram_user_id",
        "update_type",
        "status",
        "processed_at",
        "created_at",
        "updated_at",
    )
    ordering = ("-processed_at",)
