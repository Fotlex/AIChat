from django.db import models


class BotSettings(models.Model):
    bot_welcome_text = models.TextField(
        "Приветственный текст (/start)", default="Добро пожаловать!"
    )
    bot_webapp_url = models.URLField(
        "Ссылка на WebApp приложении",
        max_length=512,
        default="https://t.me/your_bot/app",
    )
    bot_channel_url = models.URLField(
        "Ссылка на Telegram-канал",
        max_length=512,
        default="https://t.me/your_channel",
    )

    class Meta:
        db_table = "bot_settings"
        verbose_name = "Настройки бота"
        verbose_name_plural = "Настройки бота"
