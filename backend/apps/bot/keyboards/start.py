from aiogram.types import InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_start_keyboard(webapp_url: str, channel_url: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✨ Открыть приложение", web_app=WebAppInfo(url=webapp_url))
    builder.button(text="💎 Наш канал", url=channel_url)
    builder.adjust(1)
    return builder.as_markup()
