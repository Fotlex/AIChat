from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse

from ..models import MainButton


class MainButtonAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        if MainButton.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        if self.model.objects.exists():
            obj = self.model.objects.first()
            url = reverse(
                f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_change",
                args=[obj.pk],
            )
            return redirect(url)
        return super().changelist_view(request, extra_context)


class OtherButtonAdmin(admin.ModelAdmin):
    list_display = ("text", "callback_data")
    search_fields = ("text", "callback_data")
