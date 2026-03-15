from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select, delete
from bot.db.database import async_session, PriceAlert
from bot.services import coingecko

router = Router()


@router.message(Command("alert"))
async def cmd_alert(message: Message):
    parts = message.text.split()[1:] if message.text else []
    if len(parts) < 2:
        await message.answer(
            "📣 <b>Уведомления о цене</b>\n\n"
            "Создать: /alert BTC 50000\n"
            "  (уведомит, когда BTC пересечёт $50,000)\n\n"
            "Список: /myalerts\n"
            "Удалить: /delalert [id]",
            parse_mode="HTML",
        )
        return

    symbol = parts[0].upper()
    try:
        target = float(parts[1].replace(",", ""))
    except ValueError:
        await message.answer("❌ Неверная цена. Пример: /alert BTC 50000")
        return

    coin_id = coingecko.resolve_coin(symbol)
    if not coin_id:
        results = await coingecko.search_coin(symbol)
        if not results:
            await message.answer(f"❌ Монета {symbol} не найдена.")
            return
        coin_id = results[0]["id"]
        symbol = results[0]["symbol"].upper()

    try:
        current = await coingecko.get_price(coin_id)
        direction = "above" if target > current["price"] else "below"
    except Exception:
        direction = "above"

    async with async_session() as db:
        alert = PriceAlert(
            user_id=message.from_user.id,
            coin_id=coin_id,
            symbol=symbol,
            target_price=target,
            direction=direction,
        )
        db.add(alert)
        await db.commit()
        await db.refresh(alert)

    dir_str = "выше" if direction == "above" else "ниже"
    await message.answer(
        f"✅ Уведомление создано!\n"
        f"<b>{symbol}</b> ${target:,.2f} ({dir_str} текущей)\n"
        f"ID: <code>{alert.id}</code>",
        parse_mode="HTML",
    )


@router.message(Command("myalerts"))
async def cmd_myalerts(message: Message):
    async with async_session() as db:
        result = await db.execute(
            select(PriceAlert).where(
                PriceAlert.user_id == message.from_user.id,
                PriceAlert.triggered == False,  # noqa
            )
        )
        alerts = result.scalars().all()

    if not alerts:
        await message.answer("У тебя нет активных уведомлений.\nСоздай: /alert BTC 50000")
        return

    lines = ["📣 <b>Твои уведомления:</b>\n"]
    for a in alerts:
        dir_str = "🔺 выше" if a.direction == "above" else "🔻 ниже"
        lines.append(f"<code>{a.id}</code>. <b>{a.symbol}</b> ${a.target_price:,.2f} ({dir_str})")

    await message.answer("\n".join(lines) + "\n\nУдалить: /delalert [id]", parse_mode="HTML")


@router.message(Command("delalert"))
async def cmd_delalert(message: Message):
    parts = message.text.split()[1:] if message.text else []
    if not parts:
        await message.answer("Использование: /delalert [id]\nСписок: /myalerts")
        return
    try:
        alert_id = int(parts[0])
    except ValueError:
        await message.answer("❌ ID должен быть числом.")
        return

    async with async_session() as db:
        result = await db.execute(
            select(PriceAlert).where(
                PriceAlert.id == alert_id,
                PriceAlert.user_id == message.from_user.id,
            )
        )
        alert = result.scalar_one_or_none()
        if not alert:
            await message.answer("❌ Уведомление не найдено.")
            return
        await db.delete(alert)
        await db.commit()

    await message.answer(f"✅ Уведомление <code>{alert_id}</code> удалено.", parse_mode="HTML")
