from django.contrib import admin

from apps.notifications.models import NotificationEvent, ReminderEvent


@admin.register(NotificationEvent)
class NotificationEventAdmin(admin.ModelAdmin):
    list_display = ("event_type", "channel", "recipient", "user", "status", "due_at", "attempts")
    list_filter = ("channel", "status", "event_type", "due_at")
    search_fields = ("event_type", "title", "body", "recipient", "user__username", "car__plate_number")
    autocomplete_fields = ("user", "car")
    list_select_related = ("user", "car")
    readonly_fields = ("id", "created_at", "updated_at", "sent_at", "last_attempt_at")
    ordering = ("due_at", "-created_at")


@admin.register(ReminderEvent)
class ReminderEventAdmin(admin.ModelAdmin):
    list_display = ("title", "reminder_type", "car", "user", "status", "due_at", "odometer_due")
    list_filter = ("reminder_type", "status", "due_at")
    search_fields = ("title", "body", "car__plate_number", "car__normalized_plate_number", "user__username")
    autocomplete_fields = ("user", "car", "notification")
    list_select_related = ("user", "car", "notification")
    readonly_fields = ("id", "created_at", "updated_at", "triggered_at", "cancelled_at")
    ordering = ("due_at", "-created_at")
