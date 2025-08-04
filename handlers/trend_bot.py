import asyncio
import random

from aiogram import Router, F
from aiogram.types import Message
from keyboards.need_coins import need
from keyboards.start_search import start_search
from keyboards.trending_topics import trending_topics_kb
from models.user import User
from database import async_session_maker
from sqlmodel import select
from aiogram.types import CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from parser import register_and_extract

router = Router()

class SearchState(StatesGroup):
    waiting_for_query = State()


@router.message(F.text == "📊 Trend Bot")
async def referral_info(message: Message):
        await message.answer(
        "<b>🔍 Готов искать тренды?</b>\n\n"
            "Введи короткий запрос и получи 🔥 подборку самых популярных видео прямо сейчас.\n\n"
            "<b>Используй коины и кради твори как художник!</b>",
            parse_mode="HTML",
            reply_markup=start_search
        )


@router.callback_query(F.data == "search")
async def close_referral_message(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()

    async with async_session_maker() as session:
        user = await session.exec(
            select(User).where(User.telegram_id == callback.from_user.id)
        )
        me = user.first()

        if me.coins <= 0:
            await callback.message.answer(
                text="😞 У тебя недостаточно coins",
                parse_mode="HTML",
                reply_markup=need
            )
            return
        else:
            me.coins -= 1
            me.flag = True
            session.add(me)
            await session.commit()

    await callback.message.answer(
        "✏️ Введи тему, по которой хочешь получить трендовые видео:\n\n"
        "Или выбери из популярных тем ниже 👇",
        parse_mode="HTML",
        reply_markup=trending_topics_kb()
    )
    await state.set_state(SearchState.waiting_for_query)
    await callback.answer()


@router.callback_query(F.data == "search_d")
async def close_referral_message(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()

    async with async_session_maker() as session:
        user = await session.exec(
            select(User).where(User.telegram_id == callback.from_user.id)
        )
        me = user.first()

        if me.diamonds <=  0:
            await callback.message.answer(
                text="😞 У тебя недостаточно 💎",
                parse_mode="HTML",
                reply_markup=need
            )
            return
        else:
            me.diamonds -= 1
            me.flag = False
            session.add(me)
            await session.commit()

    await callback.message.answer(
        "✏️ Введи тему, по которой хочешь получить трендовые видео:\n\n"
        "Или выбери из популярных тем ниже 👇",
        parse_mode="HTML",
        reply_markup=trending_topics_kb()
    )
    await state.set_state(SearchState.waiting_for_query)
    await callback.answer()


@router.callback_query(F.data.startswith("topic:"))
async def handle_topic_choice(callback: CallbackQuery, state: FSMContext):
    topic = callback.data.split(":", 1)[1]

    await callback.message.delete()
    await callback.message.answer(f"🔍 Вы выбрали тему: <b>{topic}</b>", parse_mode="HTML")

    await run_query(callback.message, topic, state)
    await callback.answer()


async def run_query(message: Message, query: str, state: FSMContext):
    query = query.strip()

    progress_msg = await message.answer("🔍 Начинаю работу...")

    async def show_progress(msg: Message, steps=10):
        statuses = [
            "🔍 Анализ запроса...",
            "📡 Поиск видео...",
            "📡 Поиск видео...",
            "📡 Поиск видео...",
            "🧠 Обработка данных...",
            "🧠 Обработка данных...",
            "🧮 Расчёт ER и CR...",
            "🧮 Расчёт ER и CR...",
            "📦 Подготовка результата...",
            "✅ Завершаем..."
        ]
        try:
            for i in range(1, steps + 1):
                done = "🟢" * i
                todo = "⚪️" * (steps - i)
                percent = i * 10
                bar = f"{done}{todo} {percent}%"
                status = statuses[i - 1]
                await msg.edit_text(f"{status}\n\n{bar}")
                await asyncio.sleep(random.randint(1, 3))
        except asyncio.CancelledError:
            pass
        except Exception:
            pass

    animation_task = asyncio.create_task(show_progress(progress_msg))

    loop = asyncio.get_event_loop()
    results = await loop.run_in_executor(None, register_and_extract, query)

    animation_task.cancel()
    try:
        await animation_task
    except asyncio.CancelledError:
        pass

    if results:
        await progress_msg.edit_text("<b>Вот что нашел Тренд Бот по твоему запросу:</b>", parse_mode="HTML")

        for res in results:
            try:
                await message.answer(
                    f"🎬 <b>Видео</b>\n\n"
                    f"👁️ Просмотры: {res['views']}\n"
                    f"❤️ Лайки: {res['likes']}\n"
                    f"💬 Комментарии: {res['comments']}\n"
                    f"🔁 Репосты: {res['reposts']}\n"
                    f"💾 Сохранили: {res['saves']}\n"
                    f"🧠 ER/View: {res['er']}\n"
                    f"📈 CR/View: {res['cr']}\n\n"
                    f"📈 Оценка вирусности: {res['viral_score']}/10\n\n"
                    f"📎 <a href='https://www.instagram.com/reel/{res['short_id']}'>Смотреть в Instagram</a>",
                    parse_mode="HTML"
                )
            except Exception as e:
                await message.answer(f"⚠️ Ошибка при разборе одного из видео: {e}")
        await state.clear()
    else:
        await progress_msg.edit_text("😕 Ничего не нашлось по этой теме. Попробуй другую формулировку.")
        async with async_session_maker() as session:
            user = await session.exec(
                select(User).where(User.telegram_id == message.from_user.id)
            )
            me = user.first()
            if me.flag:
                me.coins += 1
            else:
                me.diamonds += 1
            session.add(me)
            await session.commit()


@router.message(SearchState.waiting_for_query)
async def handle_trend_query(message: Message, state: FSMContext):
    await run_query(message, message.text, state)
