from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

need = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="💰 Пополнить баланс",
                callback_data="need_coins"
            ),
            InlineKeyboardButton(
                text="❌ Закрыть",
                callback_data="close_referral"
            )
        ]
    ]
)
