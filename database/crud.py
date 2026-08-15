from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User


async def upsert_user(session: AsyncSession, tg_user) -> User:
    """کاربر رو ذخیره می‌کنه یا در صورت وجود، اطلاعاتش رو آپدیت می‌کنه."""
    result = await session.execute(select(User).where(User.user_id == tg_user.id))
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            user_id=tg_user.id,
            username=tg_user.username,
            full_name=tg_user.full_name,
        )
        session.add(user)
    else:
        user.username = tg_user.username
        user.full_name = tg_user.full_name

    await session.commit()
    return user
