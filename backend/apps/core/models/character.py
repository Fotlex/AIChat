from django.db import models

from .base import TimeStampedMixin


class Character(TimeStampedMixin):
    class GenderChoices(models.TextChoices):
        MALE = "M", "Парень"
        FEMALE = "F", "Девушка"

    name = models.CharField("Имя", max_length=128)
    gender = models.CharField(
        "Пол",
        max_length=1,
        choices=GenderChoices.choices,
        default=GenderChoices.FEMALE,
        db_index=True,
    )
    tagline = models.CharField("Теглайн", max_length=255, blank=True)
    user_story = models.TextField("История для пользователя", blank=True)
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
            models.Index(fields=["gender", "-interaction_count", "-id"]),
            models.Index(fields=["-interaction_count", "-id"]),
            models.Index(fields=["-created_at", "-id"]),
        ]

    def __str__(self):
        return self.name


class FavoriteCharacter(TimeStampedMixin):
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    character = models.ForeignKey("Character", on_delete=models.CASCADE)

    class Meta:
        db_table = "favorite_characters"
        unique_together = ("user", "character")
        indexes = [
            models.Index(fields=["user", "-created_at"]),
        ]
