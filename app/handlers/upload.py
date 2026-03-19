from aiogram import Router
from aiogram import F
from aiogram.types import Message

from app.services.users import get_user_by_telegram_id
from app.services.videos import save_video

router = Router()


@router.message(F.text == "📤 Загрузить")
async def upload_handler(message: Message):
    user = await get_user_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer("Сначала нажмите /start")
        return

    if not user.agreed_to_rules:
        await message.answer("Сначала примите правила через /start")
        return

    if user.status == "muted":
        await message.answer("Вам временно запрещена загрузка видео.")
        return

    if user.status == "banned":
        await message.answer("Вы заблокированы.")
        return

    await message.answer(
        "Отправьте одно или несколько видео.\n"
        "Они попадут на модерацию.\n"
        "За каждое одобренное видео вы получите 0.5 монеты."
    )


@router.message(F.video)
async def handle_video_upload(message: Message):
    user = await get_user_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer("Сначала нажмите /start")
        return

    if not user.agreed_to_rules:
        await message.answer("Сначала примите правила через /start")
        return

    if user.status == "muted":
        await message.answer("Вам временно запрещена загрузка видео.")
        return

    if user.status == "banned":
        await message.answer("Вы заблокированы.")
        return

    video = message.video

    saved_video, error = await save_video(
        uploader_telegram_id=message.from_user.id,
        file_id=video.file_id,
        file_unique_id=video.file_unique_id,
        duration=video.duration,
        file_size=video.file_size,
    )

    if error == "duplicate":
        await message.answer("⚠️ Это видео уже было загружено ранее.")
        return

    if error == "user_not_found":
        await message.answer("Сначала нажмите /start")
        return

    await message.answer("✅ Видео принято и отправлено на модерацию.")