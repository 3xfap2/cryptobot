"""CoinGecko API v3 — полностью бесплатно, без ключей."""
import httpx
from typing import Optional

BASE = "https://api.coingecko.com/api/v3"

COIN_IDS = {
    "BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana",
    "BNB": "binancecoin", "XRP": "ripple", "ADA": "cardano",
    "DOGE": "dogecoin", "AVAX": "avalanche-2", "DOT": "polkadot",
    "LINK": "chainlink", "MATIC": "matic-network", "TON": "the-open-network",
}


def resolve_coin(symbol: str) -> Optional[str]:
    return COIN_IDS.get(symbol.upper())


async def get_price(coin_id: str) -> dict:
    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.get(
            f"{BASE}/coins/{coin_id}",
            params={"localization": "false", "tickers": "false", "community_data": "false"},
        )
        r.raise_for_status()
        d = r.json()
        m = d["market_data"]
        return {
            "name": d["name"],
            "symbol": d["symbol"].upper(),
            "price": m["current_price"]["usd"],
            "change_24h": m["price_change_percentage_24h"],
            "change_7d": m["price_change_percentage_7d"],
            "market_cap": m["market_cap"]["usd"],
            "volume_24h": m["total_volume"]["usd"],
            "high_24h": m["high_24h"]["usd"],
            "low_24h": m["low_24h"]["usd"],
            "ath": m["ath"]["usd"],
            "image": d["image"]["small"],
        }


async def get_top10() -> list[dict]:
    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.get(
            f"{BASE}/coins/markets",
            params={
                "vs_currency": "usd",
                "order": "market_cap_desc",
                "per_page": 10,
                "page": 1,
            },
        )
        r.raise_for_status()
        return r.json()


async def get_chart_data(coin_id: str, days: int) -> dict:
    async with httpx.AsyncClient(timeout=20) as c:
        r = await c.get(
            f"{BASE}/coins/{coin_id}/market_chart",
            params={"vs_currency": "usd", "days": days},
        )
        r.raise_for_status()
        return r.json()


async def search_coin(query: str) -> list[dict]:
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.get(f"{BASE}/search", params={"query": query})
        r.raise_for_status()
        return r.json().get("coins", [])[:5]
