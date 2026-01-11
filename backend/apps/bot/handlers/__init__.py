from apps.bot.loader import dp

from . import start


def setup_handlers():
    dp.include_router(start.router)


setup_handlers()
