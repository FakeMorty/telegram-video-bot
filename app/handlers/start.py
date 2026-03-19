from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from app.services.users import get_or_create_user, accept_rules, get_user_by_telegram_id
from app.keyboards.user import main_menu, rules_kb

router = Router()


def build_referral_link(bot_username: str | None, referral_code: str) -> str:
    if bot_username:
        return f"https://t.me/{bot_username}?start={referral_code}"
    return f"Рефкод: {referral_code}"


@router.message(F.text == "/start")
async def cmd_start(message: Message):
    user, created = await get_or_create_user(message.from_user)

    if not user.agreed_to_rules:
        text = (
            "🔞 Бот 18+\n\n"
            "Запрещено загружать дубликаты, контент не по тематике и нарушать правила.\n"
            "Нажимая кнопку ниже, вы принимаете правила."
        )
        await message.answer(text, reply_markup=rules_kb())
        return

    bot_username = None
    try:
        bot_info = await message.bot.get_me()
        bot_username = bot_info.username
    except Exception:
        pass

    referral_link = build_referral_link(bot_username, user.referral_code)

    await message.answer(
        f"Добро пожаловать, {message.from_user.first_name or 'пользователь'}!\n"
        f"Ваш баланс: {user.balance} монет\n"
        f"Ваша реферальная ссылка:\n{referral_link}",
        reply_markup=main_menu()
    )


@router.callback_query(F.data == "accept_rules")
async def accept_rules_handler(callback: CallbackQuery):
    user = await accept_rules(callback.from_user.id)

    bot_username = None
    try:
        bot_info = await callback.message.bot.get_me()
        bot_username = bot_info.username
    except Exception:
        pass

    referral_link = build_referral_link(bot_username, user.referral_code)

    await callback.message.edit_text("✅ Правила приняты.")
    await callback.message.answer(
        f"Главное меню:\n\n"
        f"Ваш баланс: {user.balance} монет\n"
        f"Ваша реферальная ссылка:\n{referral_link}",
        reply_markup=main_menu()
    )
    await callback.answer()


@router.message(F.text == "👤 Профиль")
async def profile_handler(message: Message):
    user = await get_user_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer("Сначала нажмите /start")
        return

    bot_username = None
    try:
        bot_info = await message.bot.get_me()
        bot_username = bot_info.username
    except Exception:
        pass

    referral_link = build_referral_link(bot_username, user.referral_code)

    await message.answer(
        f"👤 Профиль\n\n"
        f"ID: {user.telegram_id}\n"
        f"Баланс: {user.balance} монет\n"
        f"Реферальный код: {user.referral_code}\n"
        f"Реферальная ссылка:\n{referral_link}\n"
        f"Статус: {user.status}"
    )


@router.message(F.text == "💎 Купить монеты")
async def buy_coins_handler(message: Message):
    await message.answer(
        "💎 Покупка монет скоро будет доступна.\n"
        "В следующей версии добавим оплату через Telegram Stars."
    )


@router.message(F.text == "🎁 Офферы")
async def offers_handler(message: Message):
    await message.answer(
        "🎁 Рекламные офферы скоро появятся.\n"
        "Здесь будут задания за подписку с наградой в монетах."
    )


@router.message(F.text == "👥 Рефералы")
async def referrals_handler(message: Message):
    user = await get_user_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer("Сначала нажмите /start")
        return

    bot_username = None
    try:
        bot_info = await message.bot.get_me()
        bot_username = bot_info.username
    except Exception:
        pass

    referral_link = build_referral_link(bot_username, user.referral_code)

    await message.answer(
        f"👥 Реферальная система\n\n"
        f"Приглашайте друзей по ссылке:\n{referral_link}\n\n"
        f"Награды:\n"
        f"• пригласивший: 10 монет\n"
        f"• приглашённый: 5 монет\n\n"
        f"Начисление будет после выполнения условий в следующих обновлениях."
    )