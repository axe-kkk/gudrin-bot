from aiogram import Router
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command
from bot_texts import menu_first_time_message
from keyboards.start_menu import start_menu

router = Router()

@router.message(Command("menu"))
async def start(message: Message):

    await message.answer(
        text=menu_first_time_message,
        parse_mode="HTML",
        reply_markup=start_menu
    )


