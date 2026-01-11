from django.apps import AppConfig


class BotConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.bot"
    verbose_name = "Telegram Bot Integration"

    def ready(self):
        from . import handlers  # noqa: F401
