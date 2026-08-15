import os
from dataclasses import dataclass

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


@dataclass
class Config:
    # توکن ربات رو از @BotFather بگیر و توی فایل .env بریز (متغیر BOT_TOKEN)
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "8796106296:AAGrC56tNs0BGtHLFqodW8NIx5VU59i-Los")

    # یوزرنیم کانال عضویت اجباری (باید ربات ادمین کانال باشه)
    CHANNEL_USERNAME: str = "@bot_resume"
    CHANNEL_URL: str = "https://t.me/bot_resume"

    # آدرس دیتابیس sqlite (از طریق SQLAlchemy async + aiosqlite)
    DB_URL: str = "sqlite+aiosqlite:///bot.db"

    # تنظیمات استیم
    STEAM_CC: str = "us"          # کد ریجن برای قیمت‌ها
    STEAM_LANG: str = "english"   # زبان توضیحات

    # تنظیمات جستجو
    SEARCH_RESULTS_LIMIT: int = 10
    FUZZY_SCORE_THRESHOLD: int = 45


config = Config()
