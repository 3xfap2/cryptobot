from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select, delete
from bot.db.database import async_session, Portfolio
from bot.services import coingecko

router = Router()


@router.message(Command("portfolio"))
async def cmd_portfolio(message: Message):
    parts = message.text.split()[1:] if message.text else []

    if not parts or parts[0] == "view":
        await show_portfolio(message)
        return

    if parts[0] == "add" and len(parts) >= 3:
        await add_to_portfolio(message, parts[1:])
        return

    if parts[0] == "remove" and len(parts) >= 2:
        await remove_from_portfolio(message, parts[1])
        return

    await message.answer(
        "💼 <b>Управление портфелем</b>\n\n"
        "/portfolio — просмотр\n"
        "/portfolio add BTC 0.5 45000 — добавить монету\n"
        "  (символ, количество, цена покупки)\n"
        "/portfolio remove BTC — удалить",
        parse_mode="HTML",
    )


async def show_portfolio(message: Message):
    async with async_session() as db:
        result = await db.execute(
            select(Portfolio).where(Portfolio.user_id == message.from_user.id)
        )
        items = result.scalars().all()

    if not items:
        await message.answer(
            "💼 Портфель пуст.\n\nДобавить: /portfolio add BTC 0.5 45000"
        )
        return

    msg = await message.answer("⏳ Считаю прибыль...")
    total_invested = 0.0
    total_current = 0.0
    lines = ["💼 <b>Твой портфель:</b>\n"]

    for item in items:
        try:
            data = await coingecko.get_price(item.coin_id)
            current_price = data["price"]
        except Exception:
            current_price = item.buy_price

        invested = item.amount * item.buy_price
        current = item.amount * current_price
        pnl = current - invested
        pnl_pct = (pnl / invested * 100) if invested > 0 else 0

        total_invested += invested
        total_current += current

        arrow = "🟢" if pnl >= 0 else "🔴"
        sign = "+" if pnl >= 0 else ""
        lines.append(
            f"{arrow} <b>{item.symbol}</b> × {item.amount}\n"
            f"   ${current_price:,.4f} · PnL: <code>{sign}${pnl:,.2f} ({sign}{pnl_pct:.1f}%)</code>"
        )

    total_pnl = total_current - total_invested
    total_pnl_pct = (total_pnl / total_invested * 100) if total_invested > 0 else 0
    total_arrow = "🟢" if total_pnl >= 0 else "🔴"
    sign = "+" if total_pnl >= 0 else ""

    lines.append(
        f"\n━━━━━━━━━━━━━━━━\n"
        f"{total_arrow} <b>Итого:</b>\n"
        f"Вложено: <code>${total_invested:,.2f}</code>\n"
        f"Сейчас: <code>${total_current:,.2f}</code>\n"
        f"PnL: <code>{sign}${total_pnl:,.2f} ({sign}{total_pnl_pct:.1f}%)</code>"
    )

    await msg.edit_text("\n".join(lines), parse_mode="HTML")


async def add_to_portfolio(message: Message, args: list):
    try:
        symbol = args[0].upper()
        amount = float(args[1])
        buy_price = float(args[2])
    except (IndexError, ValueError):
        await message.answer("❌ Формат: /portfolio add BTC 0.5 45000")
        return

    coin_id = coingecko.resolve_coin(symbol)
    if not coin_id:
        results = await coingecko.search_coin(symbol)
        if not results:
            await message.answer(f"❌ Монета {symbol} не найдена.")
            return
        coin_id = results[0]["id"]
        symbol = results[0]["symbol"].upper()

    async with async_session() as db:
        entry = Portfolio(
            user_id=message.from_user.id,
            coin_id=coin_id,
            symbol=symbol,
            amount=amount,
            buy_price=buy_price,
        )
        db.add(entry)
        await db.commit()

    await message.answer(
        f"✅ Добавлено в портфель:\n<b>{symbol}</b> × {amount} по ${buy_price:,.2f}",
        parse_mode="HTML",
    )


async def remove_from_portfolio(message: Message, symbol: str):
    symbol = symbol.upper()
    async with async_session() as db:
        await db.execute(
            delete(Portfolio).where(
                Portfolio.user_id == message.from_user.id,
                Portfolio.symbol == symbol,
            )
        )
        await db.commit()
    await message.answer(f"✅ {symbol} удалён из портфеля.")
