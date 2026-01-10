from django.db import models


class User(models.Model):
    telegram_id = models.BigIntegerField(
        unique=True, primary_key=True, verbose_name="Телеграм ID"
    )

    username = models.CharField("Юзернейм", max_length=64, null=True, blank=True)
    first_name = models.CharField("Имя", max_length=255, null=True, blank=True)
    last_name = models.CharField("Фамилия", max_length=255, null=True, blank=True)

    balance = models.PositiveIntegerField("Баланс", default=0)
    total_paid = models.PositiveIntegerField(verbose_name='Всего оплачено (RUB)', default=0)
    refferal_balance = models.IntegerField(default=0, verbose_name='Реферальный баланс')
    
    referrer = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="referrals",
        verbose_name="Кто пригласил",
    )

    created_at = models.DateTimeField("Дата регистрации", auto_now_add=True, blank=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)

    @property
    def is_authenticated(self):
        return True

    def __str__(self):
        return f"id: {self.telegram_id} | @{self.username or '-'}"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["-created_at"]
