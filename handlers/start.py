# handlers/start.py
from aiogram import Router
from aiogram.types import Message
from bot_texts import start_message, menu_first_time_message
from keyboards.start_continue import start_continue_keyboard
from models.user import User
from database import async_session_maker
from sqlmodel import select
from logger import *
from aiogram.types import CallbackQuery
from keyboards.start_menu import start_menu
from aiogram.filters import CommandStart, CommandObject


router = Router()


async def handle_start(message: Message, referrer_id: str | None):
    telegram_id = message.from_user.id
    username = message.from_user.username

    async with async_session_maker() as session:
        result = await session.exec(select(User).where(User.telegram_id == telegram_id))
        user = result.first()

        if not user:
            user = User(telegram_id=telegram_id, coins=10)
            session.add(user)

            if referrer_id and referrer_id.isdigit():
                ref_user = await session.exec(select(User).where(User.telegram_id == int(referrer_id)))
                ref_user = ref_user.first()
                if ref_user and ref_user.telegram_id != telegram_id:
                    ref_user.diamonds += 1
                    user.referred_by = ref_user.id
                    session.add(ref_user)

            await session.commit()
            logger.info(f"New user registered: tg_id={telegram_id}, username={username}")
        else:
            logger.info(f"User already exists: tg_id={telegram_id}, username={username}")

    await message.answer(
        text=start_message,
        parse_mode="HTML",
        reply_markup=start_continue_keyboard,
    )


@router.message(CommandStart(deep_link=True))
async def start_with_ref(message: Message, command: CommandObject):
    await handle_start(message, command.args)


@router.message(CommandStart())
async def start_no_ref(message: Message):
    await handle_start(message, None)


@router.callback_query(lambda c: c.data == "continue_main_menu")
async def show_main_menu(callback: CallbackQuery):
    try:
        await callback.message.delete()
    except Exception as e:
        pass

    await callback.message.answer(
        text=menu_first_time_message,
        parse_mode="HTML",
        reply_markup=start_menu
    )
    await callback.answer()
