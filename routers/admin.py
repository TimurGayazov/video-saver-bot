from aiogram import F, Router
from aiogram.filters import BaseFilter, Command
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from config import settings
from services.system import Metric, get_cpu, get_disk, get_memory, human_size

router = Router()

REFRESH_CALLBACK = "admin:status_refresh"


class IsRoot(BaseFilter):
    async def __call__(self, message: Message | CallbackQuery) -> bool:
        user = message.from_user
        return user is not None and user.id == settings.root_telegram_id


def make_bar(percent: float, length: int = 10) -> str:
    percent = max(0.0, min(100.0, percent))
    filled = round(percent / 100 * length)
    return "█" * filled + "░" * (length - filled)


def build_status_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Обновить", callback_data=REFRESH_CALLBACK)]
        ]
    )


def render_status_text() -> str:
    cpu = get_cpu()
    mem = get_memory()
    disk = get_disk()
    disk_free = disk.total - disk.used

    return (
        "📊 <b>Статус сервера</b>\n\n"
        f"🖥 CPU\n<code>{make_bar(cpu.percent)}</code> {cpu.percent:.0f}%\n\n"
        f"💾 RAM\n<code>{make_bar(mem.percent)}</code> {mem.percent:.0f}%\n"
        f"{human_size(mem.used)} / {human_size(mem.total)}\n\n"
        f"💽 Disk\n<code>{make_bar(disk.percent)}</code> {disk.percent:.0f}%\n"
        f"Занято: {human_size(disk.used)} | Свободно: {human_size(disk_free)}\n"
        f"Всего: {human_size(disk.total)}"
    )


@router.message(Command("status"), IsRoot())
async def status_handler(message: Message) -> None:
    await message.answer(
        text=render_status_text(),
        reply_markup=build_status_keyboard(),
    )


@router.callback_query(F.data == REFRESH_CALLBACK, IsRoot())
async def status_refresh_handler(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        text=render_status_text(),
        reply_markup=build_status_keyboard(),
    )
    await callback.answer()
