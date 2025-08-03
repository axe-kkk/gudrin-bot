from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

start_search = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🔍 Начать искать за 1 🪙",
                callback_data="search"
            )
        ],
        [
            InlineKeyboardButton(
                text="🔍 Начать искать за 1 💎",
                callback_data="search_d"
            )
        ],
        [
            InlineKeyboardButton(
                text="❌ Закрыть",
                callback_data="back"
            )
        ]
    ]
)
