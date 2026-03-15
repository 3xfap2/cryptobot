import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message, BotCommand
from bot.db.database import init_db
from bot.handlers import price, chart, alerts, portfolio, analyze

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


async def set_commands(bot: Bot):
    await bot.set_my_commands([
        BotCommand(command="start", description="🚀 Главное меню"),
        BotCommand(command="price", description="💵 Цена монеты — /price BTC"),
        BotCommand(command="chart", description="📊 График — /chart BTC 7d"),
        BotCommand(command="analyze", description="🤖 ИИ-анализ — /analyze ETH"),
        BotCommand(command="top10", description="🏆 Топ-10 монет"),
        BotCommand(command="portfolio", description="💼 Портфель"),
        BotCommand(command="alert", description="📣 Уведомление о цене"),
        BotCommand(command="myalerts", description="📋 Мои уведомления"),
    ])


async def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN is not set")

    await init_db()

    bot = Bot(token=token)
    dp = Dispatcher()

    # Routers
    dp.include_router(price.router)
    dp.include_router(chart.router)
    dp.include_router(alerts.router)
    dp.include_router(portfolio.router)
    dp.include_router(analyze.router)

    @dp.message(CommandStart())
    async def start(message: Message):
        await message.answer(
            "🚀 <b>CryptoBot</b> — твой крипто-ассистент\n\n"
            "📌 <b>Команды:</b>\n"
            "/price BTC — текущая цена\n"
            "/chart ETH 7d — график цены\n"
            "/analyze SOL — ИИ-анализ тренда\n"
            "/top10 — топ-10 монет\n"
            "/portfolio add BTC 0.5 45000 — добавить в портфель\n"
            "/portfolio — просмотр портфеля\n"
            "/alert BTC 100000 — уведомление при достижении цены\n\n"
            "⚡ Данные: CoinGecko API · Анализ: Gemini AI",
            parse_mode="HTML",
        )

    await set_commands(bot)
    logger.info("CryptoBot started!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
