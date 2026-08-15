from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# نکته مهم: API تلگرام اجازه تعیین رنگ دلخواه برای دکمه‌های Reply Keyboard رو نمی‌ده
# (رنگ دکمه‌ها کاملاً به کلاینت تلگرام کاربر بستگی دارد و از طریق بات قابل تنظیم نیست).
# برای شبیه‌سازی حس "دکمه قرمز برگشت"، از ایموجی 🔴 استفاده شده.

MAIN_MENU_SEARCH = "🔍 جستجو بازی"
MAIN_MENU_FREE_GAMES = "🎁 بازی های رایگان شده"
MAIN_MENU_COMPARE_PRICE = "💱 مقایسه قیمت در ریجن های مختلف"
MAIN_MENU_NEWS = "📰 اخبار بازی ها"
BACK_TO_MAIN = "🔴 برگشت به صفحه اصلی"


def main_menu_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text=MAIN_MENU_SEARCH)
    kb.button(text=MAIN_MENU_FREE_GAMES)
    kb.button(text=MAIN_MENU_COMPARE_PRICE)
    kb.button(text=MAIN_MENU_NEWS)
    kb.adjust(2, 2)
    return kb.as_markup(resize_keyboard=True)


def back_to_main_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text=BACK_TO_MAIN)
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)
