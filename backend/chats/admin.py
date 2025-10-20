from django.contrib import admin

from .models import Chat, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 1
    fields = ("role", "content", "created_at")
    readonly_fields = ("created_at",)


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "character", "created_at")
    search_fields = ("user__username", "user__telegram_id", "character__name")
    list_filter = ("character", "created_at")
    readonly_fields = ("created_at",)
    inlines = [MessageInline]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "chat_info", "role", "content_preview", "created_at")
    list_filter = ("role", "created_at")
    search_fields = ("content", "chat__user__username", "chat__character__name")
    list_display_links = ("id", "chat_info")

    def chat_info(self, obj):
        return str(obj.chat)

    chat_info.short_description = "Чат"

    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content

    content_preview.short_description = "Содержание"
