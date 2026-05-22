from django.contrib import admin

from ..models import Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ("role", "content", "created_at")
    can_delete = False


class ConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "character", "last_activity_at")
    list_select_related = ("user", "character")
    inlines = [MessageInline]
    readonly_fields = ("id", "created_at")


class MessageAdmin(admin.ModelAdmin):
    list_display = ("conversation", "role", "created_at")
    list_select_related = ("conversation",)
