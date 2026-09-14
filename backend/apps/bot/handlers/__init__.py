from aiogram import Router

from .start import router as start_router

parent_router = Router()
parent_router.include_router(start_router)
