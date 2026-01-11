from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from django.conf import settings

storage = RedisStorage.from_url(settings.FSM_URL)

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher(storage=storage)
