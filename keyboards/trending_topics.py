from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

popular_topics = [
    "AI", "Crypto", "Fitness", "Fashion", "Travel",
    "Self-Care", "Motivation", "Personal Growth", "Food", "Luxury Lifestyle",
    "Reels Tips", "Viral Challenges", "Aesthetic Feeds", "Photography", "Pet Content"
]

def trending_topics_kb():
    buttons = []
    row_length = 3  # 5 кнопок в каждом ряду
    for i in range(0, len(popular_topics), row_length):
        row = [
            InlineKeyboardButton(text=topic, callback_data=f"topic:{topic}")
            for topic in popular_topics[i:i + row_length]
        ]
        buttons.append(row)

    return InlineKeyboardMarkup(inline_keyboard=buttons)
