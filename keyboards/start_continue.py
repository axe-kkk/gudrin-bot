from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

start_continue_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="👉 Продолжить",
                callback_data="continue_main_menu"
            )
        ]
    ]
)
