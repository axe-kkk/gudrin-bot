from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

popular_topics = ["AI", "Crypto", "Fitness", "Fashion", "Travel"]

def trending_topics_kb():
    buttons = [
        [InlineKeyboardButton(text=topic, callback_data=f"topic:{topic}")]
        for topic in popular_topics
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
