from django.contrib import admin
from django.utils.html import format_html

from .models import Character


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ("name", "gender", "is_active", "creator", "display_photo")
    list_filter = ("gender", "is_active")
    search_fields = ("name", "description")
    list_editable = ("is_active",)

    @admin.display(description="Фото")
    def display_photo(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover;" />',
                obj.photo.url,
            )
        return "Нет фото"
