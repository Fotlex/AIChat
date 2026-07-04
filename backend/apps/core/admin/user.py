from django.contrib import admin


class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "balance", "created_at", "is_active")
    search_fields = ("username", "id")
    list_filter = ("is_active", "created_at")
    readonly_fields = ("id",)
