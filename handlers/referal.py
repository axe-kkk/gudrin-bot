from aiogram import Router, F
from aiogram.types import Message
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import settings
from models.user import User
from database import async_session_maker
from sqlmodel import select
from aiogram.types import CallbackQuery

router = Router()

def generate_referral_link(telegram_username: str | None, telegram_id: int, bot_username: str) -> str:
    return f"https://t.me/{bot_username}?start={telegram_id}"


@router.message(F.text == "👥 Рефералы")
async def referral_info(message: Message):
    referral_link = generate_referral_link(
        telegram_username=message.from_user.username,
        telegram_id=message.from_user.id,
        bot_username=settings.bot_username
    )
    async with async_session_maker() as session:
        me =  await session.exec(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        invited_users = me.first()

        result = await session.exec(
            select(User).where(User.referred_by == invited_users.id)
        )
        invited_users = result.all()
        invited_count = len(invited_users)
        print(invited_count)

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Закрыть", callback_data="close_referral")]
        ])

        await message.answer(
            f"<b>🚀 Ваша реферальная ссылка:</b>\n\n"
            f"<code>{referral_link}</code>\n\n"
            f"<b>👥 Приглашённых друзей:</b> <b>{invited_count}</b>\n\n"
            f"💰 <i>За каждого — +1 💎 на баланс!</i>\n",
            parse_mode="HTML",
            reply_markup=keyboard
        )



@router.callback_query(F.data == "close_referral")
async def close_referral_message(callback: CallbackQuery):
    await callback.message.delete()
    await callback.answer()
