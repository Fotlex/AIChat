from django.contrib import admin
from django.utils.html import format_html

from .models import Tariff


@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    list_display = ("name", "cost", "reward")

    @admin.display(description="Фото")
    def display_photo(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover;" />',
                obj.photo.url,
            )
        return "Нет фото"

