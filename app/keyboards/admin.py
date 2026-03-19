from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def moderation_kb(video_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Одобрить", callback_data=f"approve:{video_id}"),
                InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject:{video_id}")
            ]
        ]
    )


def reject_reasons_kb(video_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Дубликат", callback_data=f"reject_reason:{video_id}:duplicate")],
            [InlineKeyboardButton(text="Не по тематике", callback_data=f"reject_reason:{video_id}:offtopic")],
            [InlineKeyboardButton(text="Другое", callback_data=f"reject_reason:{video_id}:other")],
        ]
    )