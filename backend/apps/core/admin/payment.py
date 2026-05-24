from django.contrib import admin
from ..models import Tariff, Transaction

class TariffAdmin(admin.ModelAdmin):
    list_display = ("name", "cost", "reward", "is_active", "sort_order")
    list_editable = ("is_active", "sort_order")
    list_filter = ("is_active",)
    search_fields = ("name",)

class TransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "amount", "reward", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "id", "provider_payment_id")
    readonly_fields = (
        "id", "user", "tariff", "amount", "reward", 
        "status", "provider_payment_id", "created_at", "updated_at"
    )

    def has_add_permission(self, request):
        return False