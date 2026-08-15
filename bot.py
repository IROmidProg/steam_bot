import asyncio
import logging
from aiogram.client.telegram import TelegramAPIServer
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from config import config
from database.engine import async_session, init_db
from handlers import search, start, subscription
from middlewares.subscription import SubscriptionMiddleware
from services.steam_api import ensure_game_cache


async def set_commands(bot: Bot) -> None:
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="شروع / بازگشت به منوی اصلی"),
        ]
    )


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    session = AiohttpSession(
            api=TelegramAPIServer.from_base(
                "https://test.normalop-nor.workers.dev/"
            )
        )

    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        session=session,
    )
    dp = Dispatcher()

    # session_maker به همه‌ی هندلرها به عنوان آرگومان تزریق می‌شه
    dp["session_maker"] = async_session

    # میدل‌ور عضویت اجباری، روی هر پیام و هر کالبک اجرا می‌شه
    dp.message.outer_middleware(SubscriptionMiddleware())
    dp.callback_query.outer_middleware(SubscriptionMiddleware())

    dp.include_router(start.router)
    dp.include_router(subscription.router)
    dp.include_router(search.router)

    logging.info("در حال ساخت دیتابیس...")
    await init_db()

    logging.info("در حال آماده‌سازی کش بازی‌های استیم (ممکنه اولین بار کمی طول بکشه)...")
    await ensure_game_cache(async_session)

    await set_commands(bot)

    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("ربات استارت شد.")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
