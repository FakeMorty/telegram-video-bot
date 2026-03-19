from decimal import Decimal
from sqlalchemy import select
from app.database.session import SessionLocal
from app.database.models import User


async def add_balance_by_user_id(user_id: int, amount: float):
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            return None

        user.balance = Decimal(str(user.balance)) + Decimal(str(amount))
        await session.commit()
        await session.refresh(user)
        return user


async def subtract_balance_by_user_id(user_id: int, amount: float):
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            return None

        user.balance = Decimal(str(user.balance)) - Decimal(str(amount))
        await session.commit()
        await session.refresh(user)
        return user