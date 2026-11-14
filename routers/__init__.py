from aiogram import Router

from routers import admin, commands, inline, messages

router = Router()
router.include_router(admin.router)
router.include_router(commands.router)
router.include_router(messages.router)
router.include_router(inline.router)
