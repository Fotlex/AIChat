from aiogram import Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart

from apps.bot.config_cache import BotConfigCache
from apps.bot.keyboards.start import get_start_keyboard

router = Router()


@router.message(CommandStart())
async def cmd_start(message: types.Message):
    config = await BotConfigCache.get_config()
    keyboard = get_start_keyboard(
        webapp_url=config["bot_webapp_url"], channel_url=config["bot_channel_url"]
    )
    await message.answer(
        text=config["bot_welcome_text"],
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML,
    )
