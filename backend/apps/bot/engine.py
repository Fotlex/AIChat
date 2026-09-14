from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from django.conf import settings

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

_handlers_registered = False


def get_configured_dispatcher() -> Dispatcher:
    global _handlers_registered
    if not _handlers_registered:
        from .handlers import parent_router

        dp.include_router(parent_router)
        _handlers_registered = True
    return dp
