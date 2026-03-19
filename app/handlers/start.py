from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from app.services.users import get_or_create_user, accept_rules, get_user_by_telegram_id
from app.keyboards.user import main_menu, rules_kb

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    user, created = await get_or_create_user(message.from_user)

    if not user.agreed_to_rules:
        await message.answer(
            "🔞 Бот 18+\n\nНажмите кнопку ниже, чтобы принять правила.",
            reply_markup=rules_kb()
        )
        return

    await message.answer(
        f"🏠 Главное меню\nБаланс: {user.balance}",
        reply_markup=main_menu()
    )


@router.callback_query(F.data == "accept_rules")
async def accept_rules_handler(callback: CallbackQuery):
    user = await accept_rules(callback.from_user.id)

    await callback.message.edit_text("✅ Правила приняты.")
    await callback.message.answer(
        f"🏠 Главное меню\nБаланс: {user.balance}",
        reply_markup=main_menu()
    )
    await callback.answer()


@router.message(F.text == "👤 Профиль")
async def profile_handler(message: Message):
    user = await get_user_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer("Сначала нажмите /start")
        return

    await message.answer(
        f"👤 Профиль\n\n"
        f"ID: {user.telegram_id}\n"
        f"Баланс: {user.balance} монет\n"
        f"Реферальный код: {user.referral_code}\n"
        f"Статус: {user.status}"
    )


@router.message(F.text == "💎 Купить монеты")
async def buy_coins_handler(message: Message):
    await message.answer("💎 Покупка монет скоро будет доступна.")


@router.message(F.text == "🎁 Офферы")
async def offers_handler(message: Message):
    await message.answer("🎁 Офферы скоро появятся.")


@router.message(F.text == "👥 Рефералы")
async def referrals_handler(message: Message):
    user = await get_user_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer("Сначала нажмите /start")
        return

    await message.answer(
        f"👥 Реферальная система\n\n"
        f"Ваш реферальный код: {user.referral_code}\n\n"
        f"Награды:\n"
        f"• пригласивший: 10 монет\n"
        f"• приглашённый: 5 монет\n\n"
        f"Начисление будет после выполнения условий в следующих обновлениях."
    )