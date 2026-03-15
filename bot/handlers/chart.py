from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, BufferedInputFile
from bot.services import coingecko, chart_gen

router = Router()

PERIODS = {"1d": 1, "7d": 7, "30d": 30, "90d": 90, "1y": 365}


@router.message(Command("chart"))
async def cmd_chart(message: Message):
    parts = message.text.split()[1:] if message.text else []
    if not parts:
        await message.answer(
            "Использование: /chart BTC [период]\n"
            "Периоды: 1d, 7d, 30d, 90d, 1y\n"
            "Пример: /chart ETH 30d"
        )
        return

    symbol = parts[0].upper()
    period_str = parts[1].lower() if len(parts) > 1 else "7d"
    days = PERIODS.get(period_str, 7)

    coin_id = coingecko.resolve_coin(symbol)
    if not coin_id:
        results = await coingecko.search_coin(symbol)
        if results:
            coin_id = results[0]["id"]
            symbol = results[0]["symbol"].upper()
        else:
            await message.answer(f"❌ Монета <b>{symbol}</b> не найдена.", parse_mode="HTML")
            return

    msg = await message.answer(f"📊 Генерирую график {symbol} за {period_str}...")
    try:
        data = await coingecko.get_chart_data(coin_id, days)
        prices = data["prices"]
        buf = chart_gen.generate_price_chart(prices, symbol, days)
        await msg.delete()
        await message.answer_photo(
            BufferedInputFile(buf.read(), filename=f"{symbol}_{period_str}.png"),
            caption=f"📈 <b>{symbol}/USD</b> за <b>{period_str}</b>",
            parse_mode="HTML",
        )
    except Exception as e:
        await msg.edit_text(f"❌ Ошибка генерации графика: {e}")
