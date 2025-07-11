# bot.py

import asyncio
from logger import *
from aiogram import Bot, Dispatcher
from config import settings
from database import init_db
from handlers import start, menu, referal, wallet, trend_bot

bot = Bot(token=settings.bot_token)
dp = Dispatcher()

dp.include_router(start.router)
dp.include_router(menu.router)
dp.include_router(referal.router)
dp.include_router(wallet.router)
dp.include_router(trend_bot.router)

async def main():
    logger.info("Initializing database...")
    await init_db()
    logger.info("The database is ready.")

    logger.info("Launching bot...")
    await dp.start_polling(bot)
    logger.info("The bot has finished its work.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.warning("The bot was stopped manually.")