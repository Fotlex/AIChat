import time

from apps.bot.models import BotSettings


class BotConfigCache:
    _config = None
    _last_updated = 0
    TTL = 5

    @classmethod
    async def get_config(cls) -> dict:
        now = time.time()
        if cls._config is None or (now - cls._last_updated) > cls.TTL:
            config = await BotSettings.objects.values(
                "bot_welcome_text", "bot_webapp_url", "bot_channel_url"
            ).afirst()

            if config:
                cls._config = config
            else:
                cls._config = {
                    "bot_welcome_text": "Добро пожаловать в AIChat!",
                    "bot_webapp_url": "https://t.me/your_bot/app",
                    "bot_channel_url": "https://t.me/your_channel",
                }
            cls._last_updated = now
        return cls._config
