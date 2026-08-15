from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import config
from keyboards.inline import game_link_kb, games_list_kb
from keyboards.reply import (
    BACK_TO_MAIN,
    MAIN_MENU_COMPARE_PRICE,
    MAIN_MENU_FREE_GAMES,
    MAIN_MENU_NEWS,
    MAIN_MENU_SEARCH,
    back_to_main_kb,
    main_menu_kb,
)
from services.fuzzy_search import rank_games
from services.steam_api import build_caption, get_app_details, get_cached_games
from states.search_states import SearchStates
from utils.texts import (
    ASK_GAME_NAME_TEXT,
    BACK_TO_MAIN_TEXT,
    COMING_SOON_TEXT,
    DETAILS_ERROR_TEXT,
    FOUND_GAMES_TEXT,
    NOT_FOUND_TEXT,
)

router = Router()


@router.message(F.text == MAIN_MENU_SEARCH)
async def start_search(message: Message, state: FSMContext) -> None:
    await state.set_state(SearchStates.waiting_for_query)
    await message.answer(ASK_GAME_NAME_TEXT, reply_markup=back_to_main_kb())


@router.message(F.text.in_({MAIN_MENU_FREE_GAMES, MAIN_MENU_COMPARE_PRICE, MAIN_MENU_NEWS}))
async def not_ready_yet(message: Message) -> None:
    # این سه قابلیت طبق درخواست کاربر بعداً تکمیل می‌شن
    await message.answer(COMING_SOON_TEXT)


@router.message(F.text == BACK_TO_MAIN)
async def back_to_main(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(BACK_TO_MAIN_TEXT, reply_markup=main_menu_kb())


@router.message(SearchStates.waiting_for_query)
async def process_search_query(message: Message) -> None:
    query = (message.text or "").strip()
    if not query:
        return

    games = get_cached_games()
    results = rank_games(
        query,
        games,
        limit=config.SEARCH_RESULTS_LIMIT,
        threshold=config.FUZZY_SCORE_THRESHOLD,
    )

    if not results:
        await message.answer(NOT_FOUND_TEXT.format(query=query), reply_markup=back_to_main_kb())
        return

    # کیبورد پایین صفحه (دکمه برگشت) دست‌نخورده می‌مونه، فقط زیر پیام لیست اینلاین اضافه می‌شه
    await message.answer(FOUND_GAMES_TEXT.format(query=query), reply_markup=games_list_kb(results))


@router.callback_query(F.data.startswith("game:"))
async def show_game_details(callback: CallbackQuery) -> None:
    appid = int(callback.data.split(":", 1)[1])
    await callback.answer()

    details = await get_app_details(appid)
    if not details:
        await callback.message.answer(DETAILS_ERROR_TEXT)
        return

    caption = build_caption(details)
    header_image = details.get("header_image")

    if header_image:
        await callback.message.answer_photo(
            photo=header_image,
            caption=caption,
            reply_markup=game_link_kb(appid),
        )
    else:
        await callback.message.answer(caption, reply_markup=game_link_kb(appid))
