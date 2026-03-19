import asyncio
import os
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from app.config import BOT_TOKEN, WEBHOOK_PATH, WEBHOOK_URL
from app.database.base import Base
from app.database.session import engine
from app import bot as bot_module


async def healthcheck(request: web.Request):
    return web.Response(text="OK")


async def debug_webhook(request: web.Request):
    print("Webhook request received")
    return web.Response(text="Webhook endpoint is alive")


async def on_startup(bot: Bot):
    print("on_startup called")

    await bot.set_webhook(WEBHOOK_URL)
    webhook_info = await bot.get_webhook_info()

    print("Webhook set:", WEBHOOK_URL)
    print("Webhook info url:", webhook_info.url)
    print("Pending updates:", webhook_info.pending_update_count)

    me = await bot.get_me()
    print(f"Bot connected: @{me.username} ({me.id})")


async def on_shutdown(bot: Bot):
    print("on_shutdown called")
    await bot.delete_webhook()
    await bot.session.close()


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database initialized")


async def main():
    print("Application starting...")

    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is missing")

    if not WEBHOOK_URL:
        raise ValueError("WEBHOOK_URL is missing")

    print("WEBHOOK_PATH =", WEBHOOK_PATH)
    print("WEBHOOK_URL =", WEBHOOK_URL)

    await create_tables()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    bot_module.register_handlers(dp)
    print("Handlers registered")

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    app = web.Application()

    app.router.add_get("/", healthcheck)
    app.router.add_get("/health", healthcheck)
    app.router.add_get("/debug-webhook", debug_webhook)

    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    runner = web.AppRunner(app)
    await runner.setup()

    port = int(os.getenv("PORT", 8000))
    site = web.TCPSite(runner, host="0.0.0.0", port=port)
    await site.start()

    print(f"Bot is running on port {port}")

    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())