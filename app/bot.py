from aiogram import Dispatcher

from app.handlers.start import router as start_router
from app.handlers.watch import router as watch_router
from app.handlers.upload import router as upload_router
from app.handlers.admin import router as admin_router


def register_handlers(dp: Dispatcher):
    dp.include_router(start_router)
    dp.include_router(watch_router)
    dp.include_router(upload_router)
    dp.include_router(admin_router)