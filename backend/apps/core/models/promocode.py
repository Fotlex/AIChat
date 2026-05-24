from django.db import models
from .base import TimeStampedMixin

class Promocode(TimeStampedMixin):
    code = models.CharField("Промокод", max_length=32, unique=True)
    reward = models.PositiveIntegerField("Награда (монеты)")
    is_active = models.BooleanField("Активен", default=True)
    max_uses = models.PositiveIntegerField("Макс. использований", default=1)
    current_uses = models.PositiveIntegerField("Использовано", default=0)
    expires_at = models.DateTimeField("Истекает", null=True, blank=True)

    class Meta:
        db_table = "promocodes"
        verbose_name = "Промокод"
        verbose_name_plural = "Промокоды"

class PromocodeUsage(TimeStampedMixin):
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    promocode = models.ForeignKey(Promocode, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "promocode")