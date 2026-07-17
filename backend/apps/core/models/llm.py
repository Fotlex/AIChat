from django.db import models

from .base import TimeStampedMixin


class LLMConfiguration(TimeStampedMixin):
    name = models.CharField("Название в UI", max_length=64, unique=True)
    provider_code = models.CharField("Код провайдера", max_length=128)
    cost_per_request = models.PositiveIntegerField("Стоимость запроса", default=1)
    context_window_size = models.PositiveIntegerField("Размер контекста", default=4096)
    is_active = models.BooleanField("Доступна", default=True)

    class Meta:
        db_table = "llm_configurations"
        verbose_name = "Конфигурация LLM"
        verbose_name_plural = "Конфигурации LLM"

    def __str__(self):
        return self.name
