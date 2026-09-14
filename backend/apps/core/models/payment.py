from django.db import models

from .base import TimeStampedMixin, UUIDMixin


class Transaction(UUIDMixin, TimeStampedMixin):
    class StatusChoices(models.TextChoices):
        PENDING = "pending", "Ожидает оплаты"
        SUCCESS = "success", "Оплачено"
        FAILED = "failed", "Ошибка / Отмена"

    user = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="transactions"
    )
    tariff = models.ForeignKey(
        "Tariff", on_delete=models.SET_NULL, null=True, blank=True
    )

    amount = models.DecimalField("Сумма к оплате", max_digits=10, decimal_places=2)
    reward = models.PositiveIntegerField("Монет к начислению")

    status = models.CharField(
        "Статус",
        max_length=16,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
    )
    provider_payment_id = models.CharField(
        "ID платежа YooKassa", max_length=255, blank=True, db_index=True
    )

    class Meta:
        db_table = "transactions"
        verbose_name = "Транзакция"
        verbose_name_plural = "Транзакции"
        indexes = [
            models.Index(fields=["provider_payment_id"]),
            models.Index(fields=["user", "-created_at"]),
        ]

    def __str__(self):
        return f"Транзакция {self.id} - {self.get_status_display()}"


class Tariff(TimeStampedMixin):
    name = models.CharField("Название", max_length=128)
    cost = models.DecimalField("Стоимость (Руб)", max_digits=10, decimal_places=2)
    reward = models.PositiveIntegerField("Количество монет")
    photo = models.ImageField("Иконка", upload_to="tariffs/", blank=True, null=True)
    is_active = models.BooleanField("Активен", default=True)
    sort_order = models.PositiveIntegerField("Порядок сортировки", default=0)

    class Meta:
        db_table = "tariffs"
        verbose_name = "Тариф"
        verbose_name_plural = "Тарифы"
        ordering = ["sort_order", "cost"]

    def __str__(self):
        return f"{self.name} - {self.cost} руб."
