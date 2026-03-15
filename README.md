# CryptoBot 🚀

Telegram-бот для отслеживания криптовалют с ИИ-аналитикой.

## Возможности

| Команда | Описание |
|---------|----------|
| `/price BTC` | Текущая цена, 24h/7d изменение, капитализация |
| `/chart ETH 30d` | Красивый график цены за период |
| `/analyze SOL` | ИИ-анализ тренда через Gemini |
| `/top10` | Топ-10 монет по капитализации |
| `/portfolio add BTC 0.5 45000` | Добавить монету в портфель |
| `/portfolio` | Просмотр портфеля с PnL |
| `/alert BTC 100000` | Уведомление при достижении цены |
| `/myalerts` | Список активных уведомлений |

## Стек

- **Python 3.11** + aiogram 3.x
- **CoinGecko API** (бесплатно, без ключей)
- **Gemini 1.5 Flash** (ИИ-анализ, бесплатный tier)
- **SQLite** + SQLAlchemy
- **Matplotlib** (генерация графиков)
- Docker + docker-compose

## Быстрый старт

```bash
# 1. Скопируй .env
cp .env.example .env

# 2. Заполни BOT_TOKEN и GEMINI_API_KEY в .env
# BOT_TOKEN — от @BotFather
# GEMINI_API_KEY — https://aistudio.google.com/apikey (бесплатно)

# 3. Запуск через Docker
docker-compose up -d

# Или локально:
pip install -r requirements.txt
python -m bot.main
```

## Получить Gemini API ключ

1. Зайди на https://aistudio.google.com/apikey
2. Нажми "Create API key"
3. Скопируй в `.env` → `GEMINI_API_KEY=`
