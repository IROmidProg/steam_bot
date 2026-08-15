from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware, Bot
from aiogram.types import CallbackQuery, Message, TelegramObject

from config import config
from keyboards.inline import force_sub_kb
from utils.texts import FORCE_SUB_TEXT, NOT_SUBSCRIBED_ALERT

MEMBER_STATUSES = ("member", "administrator", "creator")


class SubscriptionMiddleware(BaseMiddleware):
    """
    قبل از هر هندلر (روی Message و CallbackQuery) چک می‌کنه که کاربر عضو کانال هست یا نه.
    اگه عضو نبود، پیام/پاپ‌آپ عضویت اجباری رو نشون می‌ده و اجازه نمی‌ده به هندلر اصلی برسه.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if not isinstance(event, (Message, CallbackQuery)):
            return await handler(event, data)

        user = event.from_user
        if user is None:
            return await handler(event, data)

        # اجازه بده خود دکمه‌ی «تایید عضویت» به هندلر مخصوص خودش برسه
        # (اون هندلر خودش دوباره وضعیت عضویت رو چک می‌کنه)
        if isinstance(event, CallbackQuery) and event.data == "check_subscription":
            return await handler(event, data)

        bot: Bot = data["bot"]
        try:
            member = await bot.get_chat_member(config.CHANNEL_USERNAME, user.id)
            is_subscribed = member.status in MEMBER_STATUSES
        except Exception:
            # مثلا اگه بات ادمین کانال نباشه یا خطای شبکه بخوره
            is_subscribed = False

        if is_subscribed:
            return await handler(event, data)

        if isinstance(event, Message):
            await event.answer(FORCE_SUB_TEXT, reply_markup=force_sub_kb())
        elif isinstance(event, CallbackQuery):
            await event.answer(NOT_SUBSCRIBED_ALERT, show_alert=True)

        return None
