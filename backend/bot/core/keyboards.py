from aiogram.types import InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from apps.core.models import MainButton, OtherButton

async def get_main_keyboard() -> InlineKeyboardMarkup:
    main_btns = await MainButton.objects.afirst()
    has_others = await OtherButton.objects.aexists()
    
    builder = InlineKeyboardBuilder()
    
    if main_btns:
        builder.button(
            text=main_btns.text_app, 
            web_app=WebAppInfo(url=main_btns.link_app)
        )
        builder.button(
            text=main_btns.text_chanel, 
            url=main_btns.link_chanel
        )
    
    if has_others:
        builder.button(
            text="⚙️ Дополнительно", 
            callback_data="open_additional_menu"
        )
        
    builder.adjust(2, 1)
    return builder.as_markup()


def get_additional_keyboard(other_btns: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    for btn in other_btns:
        builder.button(text=btn.text, callback_data=btn.callback_data)
        
    builder.button(text="⬅️ Назад", callback_data="back_to_main_menu")
    
    builder.adjust(1)
    return builder.as_markup()