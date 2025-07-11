from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

start_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📊 Trend Bot")],
        [KeyboardButton(text="💳 Баланс")],
        [KeyboardButton(text="👥 Рефералы")],
        [KeyboardButton(text="📤 Вывод")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие"
)