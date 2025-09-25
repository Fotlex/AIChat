from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.models import User as AuthUser

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "telegram_id",
        "username",
        "first_name",
        "balance",
        "referrer",
        "created_at",
    )
    search_fields = ("telegram_id", "username", "first_name")
    list_filter = ("created_at",)
    readonly_fields = (
        "telegram_id",
        "username",
        "first_name",
        "last_name",
        "referrer",
        "created_at",
        "updated_at",
    )
    fieldsets = (
        (
            "Основная информация (только чтение)",
            {"fields": ("telegram_id", "username", "first_name", "last_name")},
        ),
        ("Финансы и Рефералы", {"fields": ("balance", "referrer")}),
        ("Даты (только чтение)", {"fields": ("created_at", "updated_at")}),
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.unregister(AuthUser)
admin.site.unregister(Group)
