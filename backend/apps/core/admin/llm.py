from django.contrib import admin


class LLMConfigurationAdmin(admin.ModelAdmin):
    list_display = ("name", "provider_code", "cost_per_request", "is_active")
