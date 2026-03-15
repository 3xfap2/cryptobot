"""ИИ-аналитика через Gemini 1.5 Flash (бесплатный tier)."""
import os
import httpx
import json

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-1.5-flash:generateContent?key={key}"
)

PROMPT = """Ты — эксперт по криптовалютам. Дай краткий технический анализ на русском языке (4-6 предложений).

Монета: {name} ({symbol})
Цена: ${price:,.2f}
Изменение 24h: {change_24h:+.2f}%
Изменение 7d: {change_7d:+.2f}%
Капитализация: ${market_cap:,.0f}
Объём 24h: ${volume_24h:,.0f}
ATH: ${ath:,.2f}

Обязательно: краткое мнение (бычий/медвежий/нейтральный), ключевые уровни, что стоит отслеживать.
Используй emoji для наглядности. Не давай финансовых советов — только анализ."""


async def analyze_coin(data: dict) -> str:
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        return "⚠️ GEMINI_API_KEY не задан"

    prompt = PROMPT.format(**data)
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    async with httpx.AsyncClient(timeout=30) as c:
        try:
            r = await c.post(GEMINI_URL.format(key=key), json=payload)
            r.raise_for_status()
            result = r.json()
            return result["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            return f"⚠️ Ошибка анализа: {e}"
