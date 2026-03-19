from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from app.config import ADMINS
from app.keyboards.admin import moderation_kb, reject_reasons_kb
from app.services.videos import (
    get_next_pending_video,
    approve_video,
    reject_video,
    get_video_with_uploader,
)
from app.services.balance import add_balance_by_user_id

router = Router()


async def send_next_pending(message_or_callback, bot: Bot):
    video = await get_next_pending_video()

    if not video:
        if hasattr(message_or_callback, "message") and message_or_callback.message:
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


@router.message(Command("admin"))
async def admin_panel(message: Message, bot: Bot):
    if not message.from_user:
        await message.answer("Не удалось определить пользователя.")
        return

    if message.from_user.id not in ADMINS:
        await message.answer("Нет доступа.")
        return

    await message.answer("Открываю очередь модерации...")
    await send_next_pending(message, bot)


@router.callback_query(F.data.startswith("approve:"))
async def approve_handler(callback: CallbackQuery, bot: Bot):
    if not callback.from_user:
        await callback.answer("Не удалось определить пользователя.", show_alert=True)
        return

    if callback.from_user.id not in ADMINS:
        await callback.answer("Нет доступа.", show_alert=True)
        return

    if not callback.data:
        await callback.answer("Некорректные данные.", show_alert=True)
        return

    if not callback.message:
        await callback.answer("Сообщение не найдено.", show_alert=True)
        return

    try:
        video_id = int(callback.data.split(":")[1])
    except (IndexError, ValueError):
        await callback.answer("Некорректный ID видео.", show_alert=True)
        return

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
            chat_id=uploader.telegram_id,
            text=f"✅ Ваше видео #{video_id} прошло модерацию.\nНачислено 0.5 монеты."
        )
    except Exception as e:
        print("Failed to notify uploader:", repr(e))

    await callback.answer("Одобрено")
    await send_next_pending(callback, bot)


@router.callback_query(F.data.startswith("reject:"))
async def reject_handler(callback: CallbackQuery):
    if not callback.from_user:
        await callback.answer("Не удалось определить пользователя.", show_alert=True)
        return

    if callback.from_user.id not in ADMINS:
        await callback.answer("Нет доступа.", show_alert=True)
        return

    if not callback.data:
        await callback.answer("Некорректные данные.", show_alert=True)
        return

    if not callback.message:
        await callback.answer("Сообщение не найдено.", show_alert=True)
        return

    try:
        video_id = int(callback.data.split(":")[1])
    except (IndexError, ValueError):
        await callback.answer("Некорректный ID видео.", show_alert=True)
        return

    await callback.message.answer(
        f"Выберите причину отклонения для видео {video_id}:",
        reply_markup=reject_reasons_kb(video_id)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("reject_reason:"))
async def reject_reason_handler(callback: CallbackQuery, bot: Bot):
    if not callback.from_user:
        await callback.answer("Не удалось определить пользователя.", show_alert=True)
        return

    if callback.from_user.id not in ADMINS:
        await callback.answer("Нет доступа.", show_alert=True)
        return

    if not callback.data:
        await callback.answer("Некорректные данные.", show_alert=True)
        return

    if not callback.message:
        await callback.answer("Сообщение не найдено.", show_alert=True)
        return

    try:
        _, video_id_str, reason_code = callback.data.split(":")
        video_id = int(video_id_str)
    except (ValueError, IndexError):
        await callback.answer("Некорректные данные.", show_alert=True)
        return

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
            chat_id=uploader.telegram_id,
            text=f"❌ Ваше видео #{video_id} не прошло модерацию.\nПричина: {reason_text}"
        )
    except Exception as e:
        print("Failed to notify uploader:", repr(e))

    await callback.answer("Отклонено")
    await send_next_pending(callback, bot)