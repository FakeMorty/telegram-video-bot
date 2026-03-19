import os
from dotenv import load_dotenv

load_dotenv()


def parse_admins(value: str) -> list[int]:
    if not value:
        return []

    admins = []
    for x in value.split(","):
        x = x.strip()
        if x:
            try:
                admins.append(int(x))
            except ValueError:
                raise ValueError(f"Invalid admin ID in ADMINS: {x}")
    return admins


BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set")

ADMINS = parse_admins(os.getenv("ADMINS", ""))

WEBHOOK_BASE = os.getenv("WEBHOOK_BASE")
if not WEBHOOK_BASE:
    raise ValueError("WEBHOOK_BASE is not set")

WEBHOOK_BASE = WEBHOOK_BASE.rstrip("/")
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/webhook")

if not WEBHOOK_PATH.startswith("/"):
    WEBHOOK_PATH = f"/{WEBHOOK_PATH}"

WEBHOOK_URL = f"{WEBHOOK_BASE}{WEBHOOK_PATH}"

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./bot.db")