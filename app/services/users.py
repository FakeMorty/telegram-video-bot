import uuid
from sqlalchemy import select
from app.database.session import SessionLocal
from app.database.models import User


async def get_user_by_telegram_id(telegram_id: int):
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()


async def get_user_by_referral_code(referral_code: str):
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.referral_code == referral_code)
        )
        return result.scalar_one_or_none()


async def create_user(telegram_id: int, username: str | None, first_name: str | None, last_name: str | None):
    async with SessionLocal() as session:
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            balance=2.0,
            referral_code=str(uuid.uuid4())[:8],
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


async def get_or_create_user(tg_user):
    user = await get_user_by_telegram_id(tg_user.id)
    if user:
        return user, False

    user = await create_user(
        telegram_id=tg_user.id,
        username=tg_user.username,
        first_name=tg_user.first_name,
        last_name=tg_user.last_name,
    )
    return user, True


async def accept_rules(telegram_id: int):
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        if user:
            user.agreed_to_rules = True
            await session.commit()
            await session.refresh(user)
        return user