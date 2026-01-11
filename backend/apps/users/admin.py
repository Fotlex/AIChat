from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "telegram_id",
        "username",
        "first_name",
        "balance",
        "referred_by",
        "created_at",
    )
    search_fields = ("telegram_id", "username", "first_name")
    list_filter = ("created_at",)
    readonly_fields = (
        "telegram_id",
        "username",
        "first_name",
        "last_name",
        "referred_by",
        "created_at",
        "updated_at",
    )
    fieldsets = (
        (
            "Основная информация (только чтение)",
            {"fields": ("telegram_id", "username", "first_name", "last_name")},
        ),
        ("Финансы и Рефералы", {"fields": ("balance", "referred_by")}),
        ("Даты (только чтение)", {"fields": ("created_at", "updated_at")}),
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
