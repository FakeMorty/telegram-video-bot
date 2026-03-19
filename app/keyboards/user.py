from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎥 Смотреть"), KeyboardButton(text="📤 Загрузить")],
            [KeyboardButton(text="👤 Профиль"), KeyboardButton(text="💎 Купить монеты")],
            [KeyboardButton(text="🎁 Офферы"), KeyboardButton(text="👥 Рефералы")],
        ],
        resize_keyboard=True
    )


def rules_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Принимаю", callback_data="accept_rules")]
        ]
    )


def watch_video_kb(video_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👍", callback_data=f"like:{video_id}"),
                InlineKeyboardButton(text="👎", callback_data=f"dislike:{video_id}")
            ],
            [
                InlineKeyboardButton(text="▶ Следующее", callback_data="watch_next")
            ]
        ]
    )