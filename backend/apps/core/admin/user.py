from django.contrib import admin


class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "balance", "created_at", "is_active")
    search_fields = ("username", "email")
    list_filter = ("is_active", "created_at")
    readonly_fields = ("password_hash",)
