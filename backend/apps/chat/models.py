from django.db import models

from apps.characters.models import Character
from apps.users.models import User


class Chat(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="chats",
        verbose_name="Пользователь",
    )
    character = models.ForeignKey(
        Character,
        on_delete=models.CASCADE,
        related_name="chats",
        verbose_name="Персонаж",
    )
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    def __str__(self):
        return f"Чат между {self.user} и {self.character.name}"

    class Meta:
        verbose_name = "Чат"
        verbose_name_plural = "Чаты"
        unique_together = ("user", "character")
        ordering = ["-created_at"]


class Message(models.Model):
    class Role(models.TextChoices):
        USER = "user", "Пользователь"
        ASSISTANT = "assistant", "Ассистент"
        SYSTEM = "system", "Система"

    chat = models.ForeignKey(
        Chat, on_delete=models.CASCADE, related_name="messages", verbose_name="Чат"
    )
    role = models.CharField("Роль", max_length=10, choices=Role.choices)
    content = models.TextField("Содержание")
    created_at = models.DateTimeField("Время отправки", auto_now_add=True)

    def __str__(self):
        return f"Сообщение от {self.get_role_display()} в {self.chat_id}"

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ["created_at"]
