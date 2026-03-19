from aiogram import Dispatcher

from app.handlers.start import router as start_router
from app.handlers.watch import router as watch_router
from app.handlers.upload import router as upload_router
from app.handlers.admin import router as admin_router


def register_handlers(dp: Dispatcher):
    print("Including start router...")
    dp.include_router(start_router)

    print("Including watch router...")
    dp.include_router(watch_router)

    print("Including upload router...")
    dp.include_router(upload_router)

    print("Including admin router...")
    dp.include_router(admin_router)

    print("All routers included successfully")