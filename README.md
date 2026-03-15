# CryptoBot 🚀

Telegram-бот для отслеживания криптовалют с ИИ-аналитикой тренда.

## Что это?

Полноценный крипто-ассистент в Telegram. Показывает цены, строит красивые графики через Matplotlib, ведёт портфель с PnL и отправляет уведомления при достижении целевой цены. ИИ-анализ тренда — через Gemini 1.5 Flash.

Данные берёт из **CoinGecko API** — полностью бесплатно, без API-ключей.

## Команды

| Команда | Что делает |
|---------|------------|
| `/price BTC` | Цена, 24h/7d изменение, капитализация, объём, ATH |
| `/chart ETH 30d` | График цены за 1d/7d/30d/90d/1y с moving average |
| `/analyze SOL` | ИИ-анализ тренда: бычий/медвежий, ключевые уровни |
| `/top10` | Топ-10 монет по капитализации |
| `/portfolio add BTC 0.5 45000` | Добавить позицию в портфель |
| `/portfolio` | Портфель с текущим PnL по каждой монете |
| `/alert BTC 100000` | Уведомление когда цена пересечёт отметку |
| `/myalerts` | Список активных уведомлений |
| `/delalert [id]` | Удалить уведомление |

## Стек

| Технология | Зачем |
|---|---|
| Python 3.11 + aiogram 3.x | Telegram Bot |
| CoinGecko API v3 | Цены, графики, рынок (бесплатно) |
| Gemini 1.5 Flash | ИИ-анализ тренда (бесплатный tier) |
| SQLAlchemy + SQLite | Хранение портфеля и алертов |
| Matplotlib | Генерация графиков → PNG |
| Docker + docker-compose | Деплой |

## Архитектура

```
bot/
├── handlers/       # Обработчики команд (/price, /chart, /alert...)
├── services/
│   ├── coingecko.py    # CoinGecko API клиент
│   ├── ai_analysis.py  # Gemini prompt + парсинг
│   └── chart_gen.py    # Matplotlib → BytesIO
└── db/
    └── database.py     # SQLAlchemy модели (Portfolio, PriceAlert)
```

## Быстрый старт

```bash
cp .env.example .env
# BOT_TOKEN    → от @BotFather в Telegram
# GEMINI_API_KEY → https://aistudio.google.com/apikey (бесплатно)

# Docker
docker-compose up -d

# Или локально
pip install -r requirements.txt
python -m bot.main
```
