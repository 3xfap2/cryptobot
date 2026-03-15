from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from bot.services import coingecko, ai_analysis

router = Router()


@router.message(Command("analyze"))
async def cmd_analyze(message: Message):
    parts = message.text.split()[1:] if message.text else []
    if not parts:
        await message.answer("Использование: /analyze BTC")
        return

    symbol = parts[0].upper()
    coin_id = coingecko.resolve_coin(symbol)
    if not coin_id:
        results = await coingecko.search_coin(symbol)
        if not results:
            await message.answer(f"❌ Монета {symbol} не найдена.")
            return
        coin_id = results[0]["id"]
        symbol = results[0]["symbol"].upper()

    msg = await message.answer(f"🤖 Анализирую <b>{symbol}</b>...", parse_mode="HTML")
    try:
        data = await coingecko.get_price(coin_id)
        analysis = await ai_analysis.analyze_coin(data)
        await msg.edit_text(
            f"🤖 <b>ИИ-анализ {symbol}</b>\n\n{analysis}",
            parse_mode="HTML",
        )
    except Exception as e:
        await msg.edit_text(f"❌ Ошибка: {e}")
