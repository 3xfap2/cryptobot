from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from bot.services import coingecko

router = Router()

def _fmt_price(data: dict) -> str:
    ch24 = data["change_24h"] or 0
    ch7 = data["change_7d"] or 0
    arrow = "🟢" if ch24 >= 0 else "🔴"
    sign24 = "+" if ch24 >= 0 else ""
    sign7 = "+" if ch7 >= 0 else ""

    cap = data["market_cap"]
    cap_str = f"${cap/1e9:.2f}B" if cap >= 1e9 else f"${cap/1e6:.1f}M"
    vol = data["volume_24h"]
    vol_str = f"${vol/1e9:.2f}B" if vol >= 1e9 else f"${vol/1e6:.1f}M"

    return (
        f"{arrow} <b>{data['name']} ({data['symbol']})</b>\n\n"
        f"💵 <b>${data['price']:,.4f}</b>\n\n"
        f"📈 24h:  <code>{sign24}{ch24:.2f}%</code>\n"
        f"📅 7d:   <code>{sign7}{ch7:.2f}%</code>\n\n"
        f"📊 Капитализация: <code>{cap_str}</code>\n"
        f"💧 Объём 24h: <code>{vol_str}</code>\n"
        f"🔺 High 24h: <code>${data['high_24h']:,.4f}</code>\n"
        f"🔻 Low 24h:  <code>${data['low_24h']:,.4f}</code>\n"
        f"🏆 ATH: <code>${data['ath']:,.4f}</code>"
    )


@router.message(Command("price"))
async def cmd_price(message: Message):
    args = message.text.split()[1:] if message.text else []
    if not args:
        await message.answer("Использование: /price BTC\nПример: /price ETH")
        return

    symbol = args[0].upper()
    coin_id = coingecko.resolve_coin(symbol)
    if not coin_id:
        # Try direct search
        results = await coingecko.search_coin(symbol)
        if results:
            coin_id = results[0]["id"]
        else:
            await message.answer(f"❌ Монета <b>{symbol}</b> не найдена.")
            return

    msg = await message.answer("⏳ Получаю данные...")
    try:
        data = await coingecko.get_price(coin_id)
        await msg.edit_text(_fmt_price(data), parse_mode="HTML")
    except Exception as e:
        await msg.edit_text(f"❌ Ошибка: {e}")


@router.message(Command("top10"))
async def cmd_top10(message: Message):
    msg = await message.answer("⏳ Загружаю топ-10...")
    try:
        coins = await coingecko.get_top10()
        lines = ["🏆 <b>Топ 10 криптовалют по капитализации</b>\n"]
        for i, c in enumerate(coins, 1):
            ch = c.get("price_change_percentage_24h") or 0
            arrow = "🟢" if ch >= 0 else "🔴"
            price = c["current_price"]
            price_str = f"${price:,.2f}" if price >= 1 else f"${price:.4f}"
            lines.append(f"{i}. {arrow} <b>{c['symbol'].upper()}</b> {price_str} <code>{ch:+.1f}%</code>")
        await msg.edit_text("\n".join(lines), parse_mode="HTML")
    except Exception as e:
        await msg.edit_text(f"❌ Ошибка: {e}")
