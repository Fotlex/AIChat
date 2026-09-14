from django.db import models

from .base import TimeStampedMixin, UUIDMixin


class Conversation(UUIDMixin, TimeStampedMixin):
    user = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="conversations"
    )
    character = models.ForeignKey(
        "Character", on_delete=models.CASCADE, related_name="conversations"
    )
    llm_config = models.ForeignKey("LLMConfiguration", on_delete=models.RESTRICT)

    last_message_preview = models.CharField("Превью", max_length=255, blank=True)
    last_activity_at = models.DateTimeField("Последняя активность", auto_now_add=True)

    class Meta:
        db_table = "conversations"
        unique_together = ("user", "character")
        verbose_name = "Беседа"
        verbose_name_plural = "Беседы"
        indexes = [
            models.Index(fields=["user", "-last_activity_at", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.user.username} x {self.character.name}"


class Message(TimeStampedMixin):
    class RoleChoices(models.TextChoices):
        USER = "user", "Пользователь"
        ASSISTANT = "assistant", "Ассистент"
        SYSTEM = "system", "Система"

    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    role = models.CharField("Роль", max_length=16, choices=RoleChoices.choices)
    content = models.TextField("Содержимое")

    class Meta:
        db_table = "messages"
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        indexes = [
            models.Index(fields=["conversation", "-id"]),
        ]

    def __str__(self):
        return f"{self.role}: {self.content[:20]}"
