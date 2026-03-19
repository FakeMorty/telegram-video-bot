from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

router = Router()


@router.message(F.text == "🎥 Смотреть")
async def watch_handler(message: Message):
    await message.answer("🎬 Кнопка Смотреть нажата")


@router.callback_query(F.data == "watch_next")
async def watch_next_handler(callback: CallbackQuery):
    await callback.answer("Следующее видео")