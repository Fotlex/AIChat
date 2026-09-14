from django.db import models

from .base import TimeStampedMixin


class Referral(TimeStampedMixin):
    referrer = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="referrals_made", db_index=True
    )
    referred = models.OneToOneField(
        "User", on_delete=models.CASCADE, related_name="referral_origin"
    )
    reward_amount = models.PositiveIntegerField("Выданная награда", default=100)

    class Meta:
        db_table = "referrals"
        verbose_name = "Реферал"
        verbose_name_plural = "Рефералы"
