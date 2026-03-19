from decimal import Decimal
from aiogram import Router
from aiogram import F
from aiogram.types import Message, CallbackQuery

from app.services.users import get_user_by_telegram_id
from app.services.videos import get_random_video_for_user, mark_video_viewed, rate_video
from app.services.balance import subtract_balance_by_user_id
from app.keyboards.user import watch_video_kb

router = Router()


async def send_random_video(target_message: Message):
    user = await get_user_by_telegram_id(target_message.from_user.id)
    if not user:
        await target_message.answer("Сначала нажмите /start")
        return

    if not user.agreed_to_rules:
        await target_message.answer("Сначала примите правила через /start")
        return

    if user.status == "banned":
        await target_message.answer("Вы заблокированы.")
        return

    if Decimal(str(user.balance)) < Decimal("1"):
        await target_message.answer(
            "❌ Недостаточно монет для просмотра.\n"
            "Загрузите своё видео или купите монеты."
        )
        return

    video, error = await get_random_video_for_user(target_message.from_user.id)

    if error == "no_videos":
        await target_message.answer(
            "В базе больше нет новых видео для вас.\n"
            "Самое время загрузить своё."
        )
        return

    if error == "user_not_found":
        await target_message.answer("Сначала нажмите /start")
        return

    sent = await target_message.answer_video(
        video=video.telegram_file_id,
        caption=f"Видео #{video.id}",
        reply_markup=watch_video_kb(video.id)
    )

    if sent:
        await subtract_balance_by_user_id(user.id, 1.0)
        await mark_video_viewed(target_message.from_user.id, video.id)


@router.message(F.text == "🎥 Смотреть")
async def watch_handler(message: Message):
    await send_random_video(message)


@router.callback_query(F.data == "watch_next")
async def watch_next_handler(callback: CallbackQuery):
    await callback.answer()
    await send_random_video(callback.message)


@router.callback_query(F.data.startswith("like:"))
async def like_handler(callback: CallbackQuery):
    video_id = int(callback.data.split(":")[1])
    await rate_video(callback.from_user.id, video_id, 1)
    await callback.answer("Лайк поставлен")


@router.callback_query(F.data.startswith("dislike:"))
async def dislike_handler(callback: CallbackQuery):
    video_id = int(callback.data.split(":")[1])
    await rate_video(callback.from_user.id, video_id, -1)
    await callback.answer("Дизлайк поставлен")