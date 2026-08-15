from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from database.crud import upsert_user
from keyboards.reply import main_menu_kb
from utils.texts import WELCOME_TEXT

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, session_maker) -> None:
    await state.clear()

    async with session_maker() as session:
        await upsert_user(session, message.from_user)

    await message.answer(WELCOME_TEXT, reply_markup=main_menu_kb())
