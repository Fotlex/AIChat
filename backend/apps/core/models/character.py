from django.db import models
from .base import TimeStampedMixin


class Character(TimeStampedMixin):
    name = models.CharField("Имя", max_length=128)
    tagline = models.CharField("Теглайн", max_length=255, blank=True)
    avatar = models.ImageField("Аватар", upload_to="characters/", blank=True, null=True)

    system_prompt = models.TextField("Системный промпт")
    greeting_message = models.TextField("Приветствие", blank=True)

    author = models.ForeignKey("User", on_delete=models.SET_NULL, null=True, blank=True)
    is_public = models.BooleanField("Публичный", default=True)

    interaction_count = models.PositiveIntegerField("Счетчик взаимодействий", default=0)

    class Meta:
        db_table = "characters"
        verbose_name = "Персонаж"
        verbose_name_plural = "Персонажи"
        indexes = [
            models.Index(fields=["-interaction_count", "-id"]),
            models.Index(fields=["-created_at", "-id"]),
        ]

    def __str__(self):
        return self.name
