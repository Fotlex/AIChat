from aiogram import Router, types, F
from aiogram.filters import CommandStart
from apps.core.models import OtherButton, MainButton
from bot.core.keyboards import get_main_keyboard, get_additional_keyboard

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    keyboard = await get_main_keyboard()
    
    main_btns = await MainButton.objects.afirst()
    welcome_text = main_btns.text_main

    await message.answer(
        text=welcome_text, 
        reply_markup=keyboard,
        parse_mode="HTML"
    )


@router.callback_query(F.data == "open_additional_menu")
async def process_additional_menu(callback: types.CallbackQuery):
    other_btns = [btn async for btn in OtherButton.objects.all()]
    main_btns = await MainButton.objects.afirst()
    
    if not other_btns:
        await callback.answer("Раздел пуст", show_alert=True)
        return

    keyboard = get_additional_keyboard(other_btns)
    menu_text = main_btns.text_other

    await callback.message.edit_text(
        text=menu_text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "back_to_main_menu")
async def process_back_to_main(callback: types.CallbackQuery):
    keyboard = await get_main_keyboard()
    
    main_btns = await MainButton.objects.afirst()
    welcome_text = main_btns.text_main

    await callback.message.edit_text(
        text=welcome_text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()