from django.db import models
from .base import TimeStampedMixin


class User(TimeStampedMixin):
    id = models.BigAutoField(primary_key=True)
    preferred_llm = models.ForeignKey(
        "LLMConfiguration", 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    username = models.CharField(
        "Имя пользователя", max_length=64, unique=True, db_index=True
    )
    password_hash = models.CharField("Хэш пароля", max_length=255)

    balance = models.BigIntegerField("Баланс", default=0)
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        db_table = "users"
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username
