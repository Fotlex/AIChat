from django.db import models

from .base import TimeStampedMixin


class MainButton(TimeStampedMixin):
    text_chanel = models.CharField(
        max_length=50, verbose_name="Текст на кнопке в канал", default="ТГ канал"
    )
    link_chanel = models.CharField(
        max_length=50, verbose_name="Ссылка на канал", default="https://example.com"
    )

    text_app = models.CharField(
        max_length=50, verbose_name="Текст на кнопке с приложением", default="Открыть"
    )
    link_app = models.CharField(
        max_length=50,
        verbose_name="Ссылка на приложение",
        default="https://example.com",
    )

    text_main = models.TextField(
        verbose_name="Текст при команде старт", default="------"
    )
    text_other = models.TextField(verbose_name="Текст при кнопке Дополнительно")

    class Meta:
        db_table = "main_buttons"
        verbose_name = "Основные Кнопки"
        verbose_name_plural = "Основные Кнопки"


class OtherButton(TimeStampedMixin):
    text = models.CharField(
        max_length=50, default="...", verbose_name="Текст на кнопке"
    )
    callback_data = models.CharField(
        max_length=100, default="...", verbose_name="callback кнопки"
    )

    class Meta:
        db_table = "other_buttons"
        verbose_name = "Дополнительные Кнопки"
        verbose_name_plural = "Дополнительные Кнопки"
