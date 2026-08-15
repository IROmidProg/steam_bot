from typing import Optional

import aiohttp
from sqlalchemy import select

from config import config
from database.models import Game

GET_APP_LIST_URL = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
APP_DETAILS_URL = "https://store.steampowered.com/api/appdetails"

# لیست بازی‌ها (appid, name) توی رم نگه‌داری می‌شه تا هر جستجو نیاز به کوئری دیتابیس/شبکه نداشته باشه
_games_cache: list[tuple[int, str]] = []


async def ensure_game_cache(session_maker) -> None:
    """
    اگه جدول games_cache خالی بود، یک‌بار کامل از استیم (GetAppList) می‌گیره و ذخیره می‌کنه.
    این لیست شامل ده‌ها هزار appid هست، پس فقط یک‌بار (یا با /update_gamelist دستی) انجام می‌شه.
    """
    async with session_maker() as session:
        existing = await session.execute(select(Game.appid).limit(1))
        if existing.first():
            await load_games_into_memory(session_maker)
            return

    apps = await _fetch_app_list()
    if not apps:
        return

    async with session_maker() as session:
        objs = [Game(appid=a["appid"], name=a["name"]) for a in apps if a.get("name")]
        session.add_all(objs)
        await session.commit()

    await load_games_into_memory(session_maker)


async def refresh_game_cache(session_maker) -> int:
    """برای رفرش دستی کامل لیست بازی‌ها (مثلا با یک کامند ادمین)."""
    apps = await _fetch_app_list()
    if not apps:
        return 0

    async with session_maker() as session:
        await session.execute(Game.__table__.delete())
        objs = [Game(appid=a["appid"], name=a["name"]) for a in apps if a.get("name")]
        session.add_all(objs)
        await session.commit()

    await load_games_into_memory(session_maker)
    return len(_games_cache)


async def _fetch_app_list() -> list[dict]:
    async with aiohttp.ClientSession() as http:
        async with http.get(GET_APP_LIST_URL) as resp:
            data = await resp.json()
    return data.get("applist", {}).get("apps", [])


async def load_games_into_memory(session_maker) -> None:
    global _games_cache
    async with session_maker() as session:
        result = await session.execute(select(Game.appid, Game.name))
        _games_cache = [(row[0], row[1]) for row in result.all()]


def get_cached_games() -> list[tuple[int, str]]:
    return _games_cache


async def get_app_details(appid: int) -> Optional[dict]:
    params = {"appids": appid, "cc": config.STEAM_CC, "l": config.STEAM_LANG}
    async with aiohttp.ClientSession() as http:
        async with http.get(APP_DETAILS_URL, params=params) as resp:
            data = await resp.json()

    entry = data.get(str(appid))
    if not entry or not entry.get("success"):
        return None
    return entry.get("data")


def build_caption(details: dict) -> str:
    name = details.get("name", "-")
    is_free = details.get("is_free", False)

    if is_free:
        price_line = "🆓 رایگان"
    else:
        price_overview = details.get("price_overview")
        if price_overview:
            final = price_overview.get("final_formatted", "-")
            discount = price_overview.get("discount_percent", 0)
            if discount:
                initial = price_overview.get("initial_formatted", "-")
                price_line = f"💰 {final} (تخفیف {discount}%، قیمت اصلی: {initial})"
            else:
                price_line = f"💰 {final}"
        else:
            price_line = "💰 قیمت نامشخص / در این ریجن موجود نیست"

    genres = details.get("genres", [])
    genres_txt = ", ".join(g.get("description", "") for g in genres) or "-"

    developers = ", ".join(details.get("developers", [])) or "-"
    release = details.get("release_date", {}).get("date", "-")

    desc = (details.get("short_description") or "").strip()
    if len(desc) > 400:
        desc = desc[:400].rsplit(" ", 1)[0] + "..."

    caption = (
        f"🎮 <b>{name}</b>\n\n"
        f"{desc}\n\n"
        f"{price_line}\n"
        f"🏷 ژانر: {genres_txt}\n"
        f"👨‍💻 سازنده: {developers}\n"
        f"📅 تاریخ انتشار: {release}"
    )
    return caption
