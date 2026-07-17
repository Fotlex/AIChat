from django.contrib import admin
from django.utils import timezone

from ..models.promocode import PromocodeUsage


class PromocodeUsageInline(admin.TabularInline):
    model = PromocodeUsage
    extra = 0
    readonly_fields = ("user", "created_at")
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


class PromocodeAdmin(admin.ModelAdmin):
    list_display = ("code", "reward", "usage_stat", "is_active", "status", "expires_at")
    list_filter = ("is_active", "expires_at", "created_at")
    search_fields = ("code",)
    readonly_fields = ("current_uses",)
    inlines = [PromocodeUsageInline]

    fieldsets = (
        ("Основные настройки", {"fields": ("code", "reward", "is_active")}),
        ("Лимиты и сроки", {"fields": ("max_uses", "current_uses", "expires_at")}),
    )

    @admin.display(description="Использовано")
    def usage_stat(self, obj):
        return f"{obj.current_uses} / {obj.max_uses}"

    @admin.display(description="Статус")
    def status(self, obj):
        if not obj.is_active:
            return "🔴 Выключен"
        if obj.expires_at and obj.expires_at < timezone.now():
            return "⏰ Истек"
        if obj.current_uses >= obj.max_uses:
            return "🚫 Лимит исчерпан"
        return "🟢 Активен"


class PromocodeUsageAdmin(admin.ModelAdmin):
    list_display = ("user", "promocode", "created_at")
    list_filter = ("promocode", "created_at")
    search_fields = ("user__username", "promocode__code")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
