from django.contrib import admin
from django.utils.html import format_html


class CharacterAdmin(admin.ModelAdmin):
    list_display = ("display_avatar", "name", "interaction_count", "is_public")
    search_fields = ("name", "tagline")
    list_filter = ("is_public",)

    @admin.display(description="Аватар")
    def display_avatar(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" width="40" height="40" style="border-radius:50%; object-fit:cover;" />',
                obj.avatar.url,
            )
        return "—"
