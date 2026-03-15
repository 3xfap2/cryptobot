import os
from dataclasses import dataclass

@dataclass
class Config:
    BOT_TOKEN: str
    GEMINI_API_KEY: str
    DATABASE_URL: str = "sqlite+aiosqlite:///./crypto.db"

def get_config() -> Config:
    token = os.getenv("BOT_TOKEN")
    gemini = os.getenv("GEMINI_API_KEY")
    if not token:
        raise ValueError("BOT_TOKEN is not set")
    if not gemini:
        raise ValueError("GEMINI_API_KEY is not set")
    return Config(BOT_TOKEN=token, GEMINI_API_KEY=gemini)
