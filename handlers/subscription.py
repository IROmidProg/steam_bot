from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery

from config import config
from database.crud import upsert_user
from keyboards.reply import main_menu_kb
from utils.texts import NOT_SUBSCRIBED_ALERT, WELCOME_TEXT

router = Router()

MEMBER_STATUSES = ("member", "administrator", "creator")


@router.callback_query(F.data == "check_subscription")
async def check_subscription(callback: CallbackQuery, bot: Bot, session_maker) -> None:
    try:
        member = await bot.get_chat_member(config.CHANNEL_USERNAME, callback.from_user.id)
        is_subscribed = member.status in MEMBER_STATUSES
    except Exception:
        is_subscribed = False

    if not is_subscribed:
        await callback.answer(NOT_SUBSCRIBED_ALERT, show_alert=True)
        return

    async with session_maker() as session:
        await upsert_user(session, callback.from_user)

    try:
        await callback.message.delete()
    except Exception:
        pass

    await callback.message.answer(WELCOME_TEXT, reply_markup=main_menu_kb())
    await callback.answer("✅ عضویت شما تایید شد")
