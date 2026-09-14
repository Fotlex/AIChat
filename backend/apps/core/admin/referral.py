from django.contrib import admin


class ReferralAdmin(admin.ModelAdmin):
    list_select_related = ("referrer", "referred")

    list_display = ("referred", "referrer", "reward_amount", "created_at")
    list_filter = ("created_at",)
    search_fields = (
        "referrer__username",
        "referred__username",
        "referrer__id",
        "referred__id",
    )

    readonly_fields = ("referrer", "referred", "reward_amount", "created_at")

    raw_id_fields = ("referrer", "referred")

    def has_add_permission(self, request):
        return False
