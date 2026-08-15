from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import config

# نکته مهم: API تلگرام رنگ پس‌زمینه دکمه‌های Inline رو هم قابل تنظیم توسط بات نمی‌کنه
# (فقط ظاهر دکمه‌ها به کلاینت تلگرام کاربر بستگی دارد). برای نمایش حس "دکمه سبز تایید"،
# از ایموجی ✅ استفاده شده.


def force_sub_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="📢 عضویت در کانال", url=config.CHANNEL_URL)
    kb.button(text="✅ تایید عضویت", callback_data="check_subscription")
    kb.adjust(1)
    return kb.as_markup()


def games_list_kb(games: list[tuple[int, str]]) -> InlineKeyboardMarkup:
    """games: لیست تاپل‌های (appid, name)"""
    kb = InlineKeyboardBuilder()
    for appid, name in games:
        kb.button(text=name, callback_data=f"game:{appid}")
    kb.adjust(1)
    return kb.as_markup()


def game_link_kb(appid: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🔗 مشاهده در استیم", url=f"https://store.steampowered.com/app/{appid}")
    return kb.as_markup()
