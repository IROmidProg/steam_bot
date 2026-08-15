from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config import config
from database.models import Base

engine = create_async_engine(config.DB_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def init_db() -> None:
    """جدول‌ها رو در صورت نیاز می‌سازه (اگه از قبل وجود نداشته باشن)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
