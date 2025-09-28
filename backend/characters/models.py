import os
import uuid

from django.db import models


def character_photo_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    new_filename = f"{uuid.uuid4()}{ext}"

    return f"characters/{new_filename}"


class Character(models.Model):
    class Gender(models.TextChoices):
        MALE = "M", "Мужской"
        FEMALE = "F", "Женский"

    name = models.CharField("Имя персонажа", max_length=50, unique=True)
    gender = models.CharField(
        "Пол", max_length=1, choices=Gender.choices, default=Gender.FEMALE
    )

    system_prompt = models.TextField(
        "Системный промпт (личность)",
        help_text="Основа личности и поведения персонажа.",
    )

    photo = models.ImageField(
        "Фото персонажа", upload_to=character_photo_path, blank=True, null=True
    )

    description = models.CharField(
        "Краткое описание",
        max_length=255,
        help_text="Отображается в списке персонажей.",
    )

    welcome_message = models.TextField(
        "Приветственное сообщение",
        blank=True,
        null=True,
        help_text="Первое сообщение, которое персонаж отправит в новом чате.",
    )

    creator = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        related_name='characters',
        verbose_name="Создатель",
        null=True,
        blank=True,
    )
    
    is_active = models.BooleanField(
        "Активен",
        default=True,
        help_text="Отключенные персонажи не будут видны пользователям.",
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Персонаж"
        verbose_name_plural = "Персонажи"
        ordering = ["name"]
