from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from models.user import User
from database import async_session_maker
from sqlmodel import select
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import LabeledPrice, PreCheckoutQuery

router = Router()
CURRENCY = 'XTR'
STAR_PER_COIN = 5

from aiogram.types import CallbackQuery

@router.callback_query(F.data == "need_coins")
async def show_balance_callback(callback: CallbackQuery):
    await callback.message.delete()
    async with async_session_maker() as session:
        result = await session.exec(select(User).where(User.telegram_id == callback.from_user.id))
        user = result.first()

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💰 Купить coins", callback_data="buy_coins")],
            [InlineKeyboardButton(text="❌ Закрыть", callback_data="close_referral")]
        ])

        await callback.message.answer(
            f"💰 Ваш текущий баланс:\n"
            f"{user.coins} 🪙\n"
            f"{user.diamonds} 💎\n\n"
            f"⭐️ Курс 🪙 к Telegram Stars (XTR): 5 ⭐️ = 1 🪙",
            reply_markup=keyboard
        )


@router.message(F.text == "💳 Баланс")
async def show_balance_message(message: Message):
    async with async_session_maker() as session:
        result = await session.exec(select(User).where(User.telegram_id == message.from_user.id))
        user = result.first()

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💰 Купить 🪙", callback_data="buy_coins")],
            [InlineKeyboardButton(text="❌ Закрыть", callback_data="close_referral")]
        ])

        await message.answer(
            f"💰 Ваш текущий баланс:\n"
            f"{user.coins} 🪙\n"
            f"{user.diamonds} 💎\n\n"
            f"⭐️ Курс 🪙 к Telegram Stars (XTR): 5 ⭐️ = 1 🪙",
            reply_markup=keyboard
        )



def coins_purchase_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="10 🪙 — 50 ⭐️", callback_data="buy:10")
    builder.button(text="50 🪙 — 250 ⭐️", callback_data="buy:50")
    builder.button(text="100 🪙 — 500 ⭐️", callback_data="buy:100")
    builder.button(text="200 🪙 — 1000 ⭐️", callback_data="buy:200")
    builder.button(text="❌ Закрыть", callback_data="close_purchase")
    builder.adjust(1)
    return builder.as_markup()


@router.callback_query(F.data == "buy_coins")
async def show_buy_options(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(
        "Выберите количество 🪙, которое хотите приобрести:",
        reply_markup=coins_purchase_keyboard()
    )


@router.callback_query(F.data.startswith("buy:"))
async def process_buy_selection(callback: CallbackQuery, bot: Bot):
    amount = int(callback.data.split(":")[1])
    stars_amount = amount * STAR_PER_COIN

    prices = [LabeledPrice(label=f"{amount} 🪙", amount=stars_amount)]

    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title=f"Покупка {amount} 🪙",
        description=f"Вы покупаете {amount} 🪙 за {stars_amount} ⭐️",
        payload=f"buy_{amount}_coins",
        currency=CURRENCY,
        prices=prices,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=f"Оплатить {stars_amount} ⭐️", pay=True)],
                [InlineKeyboardButton(text="❌ Закрыть", callback_data="close_referral")]
            ]
        )
    )

    await callback.answer()


@router.callback_query(F.data == "close_purchase")
@router.callback_query(F.data == "close_referral")
async def close_message(callback: CallbackQuery):
    await callback.message.delete()
    await callback.answer()


@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def handle_successful_payment(message: Message):
    stars_paid = message.successful_payment.total_amount
    coins_purchased = stars_paid // STAR_PER_COIN

    async with async_session_maker() as session:
        result = await session.exec(select(User).where(User.telegram_id == message.from_user.id))
        user = result.first()
        if user:
            user.coins += coins_purchased
            session.add(user)
            await session.commit()

    await message.answer(f"✅ Вы успешно приобрели {coins_purchased} coins!")