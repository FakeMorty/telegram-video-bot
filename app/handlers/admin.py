from aiogram import Router
from aiogram import F
from aiogram.types import Message, CallbackQuery

from app.config import ADMINS
from app.keyboards.admin import moderation_kb, reject_reasons_kb
from app.services.videos import get_next_pending_video
from app.services.videos import approve_video
from app.services.videos import reject_video
from app.services.videos import get_video_with_uploader
from app.services.balance import add_balance_by_user_id

router = Router()


async def send_next_pending(message_or_callback, bot):
    video = await get_next_pending_video()

    if not video:
        if hasattr(message_or_callback, "message"):
            await message_or_callback.message.answer("Очередь модерации пуста.")
        else:
            await message_or_callback.answer("Очередь модерации пуста.")
        return

    caption = (
        f"🆔 Видео ID: {video.id}\n"
        f"Статус: {video.status}\n"
        f"Длительность: {video.duration_seconds or 0} сек\n"
        f"Размер: {video.file_size or 0} байт"
    )

    target = message_or_callback.message if hasattr(message_or_callback, "message") else message_or_callback
    await bot.send_video(
        chat_id=target.chat.id,
        video=video.telegram_file_id,
        caption=caption,
        reply_markup=moderation_kb(video.id)
    )


@router.message(F.text == "/admin")
async def admin_panel(message: Message, bot):
    if message.from_user.id not in ADMINS:
        await message.answer("Нет доступа.")
        return

    await message.answer("Открываю очередь модерации...")
    await send_next_pending(message, bot)


@router.callback_query(F.data.startswith("approve:"))
async def approve_handler(callback: CallbackQuery, bot):
    if callback.from_user.id not in ADMINS:
        await callback.answer("Нет доступа.", show_alert=True)
        return

    video_id = int(callback.data.split(":")[1])

    row = await get_video_with_uploader(video_id)
    if not row:
        await callback.answer("Видео не найдено.", show_alert=True)
        return

    video, uploader = row

    approved = await approve_video(video_id)
    if not approved:
        await callback.answer("Не удалось одобрить видео.", show_alert=True)
        return

    await add_balance_by_user_id(uploader.id, 0.5)

    await callback.message.answer(
        f"✅ Видео {video_id} одобрено.\n"
        f"Пользователю @{uploader.username or uploader.telegram_id} начислено 0.5 монеты."
    )

    try:
        await bot.send_message(
            uploader.telegram_id,
            f"✅ Ваше видео #{video_id} прошло модерацию.\nНачислено 0.5 монеты."
        )
    except Exception:
        pass

    await callback.answer("Одобрено")
    await send_next_pending(callback, bot)


@router.callback_query(F.data.startswith("reject:"))
async def reject_handler(callback: CallbackQuery):
    if callback.from_user.id not in ADMINS:
        await callback.answer("Нет доступа.", show_alert=True)
        return

    video_id = int(callback.data.split(":")[1])
    await callback.message.answer(
        f"Выберите причину отклонения для видео {video_id}:",
        reply_markup=reject_reasons_kb(video_id)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("reject_reason:"))
async def reject_reason_handler(callback: CallbackQuery, bot):
    if callback.from_user.id not in ADMINS:
        await callback.answer("Нет доступа.", show_alert=True)
        return

    _, video_id_str, reason_code = callback.data.split(":")
    video_id = int(video_id_str)

    reason_map = {
        "duplicate": "Дубликат",
        "offtopic": "Не по тематике",
        "other": "Другое нарушение",
    }
    reason_text = reason_map.get(reason_code, "Отклонено")

    row = await get_video_with_uploader(video_id)
    if not row:
        await callback.answer("Видео не найдено.", show_alert=True)
        return

    video, uploader = row

    rejected = await reject_video(video_id, reason_text)
    if not rejected:
        await callback.answer("Не удалось отклонить видео.", show_alert=True)
        return

    await callback.message.answer(
        f"❌ Видео {video_id} отклонено.\nПричина: {reason_text}"
    )

    try:
        await bot.send_message(
            uploader.telegram_id,
            f"❌ Ваше видео #{video_id} не прошло модерацию.\nПричина: {reason_text}"
        )
    except Exception:
        pass

    await callback.answer("Отклонено")
    await send_next_pending(callback, bot)