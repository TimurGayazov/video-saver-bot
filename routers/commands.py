import logging

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from services.widgets import send_html_widget

router = Router()


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    user_id = message.from_user.id
    await message.answer(f"Ваш Telegram ID: <code>{user_id}</code>")


@router.message(Command("id"))
async def get_user_id_handler(message: Message) -> None:
    user_id = message.from_user.id
    await message.answer(f"Ваш Telegram ID: <code>{user_id}</code>")


@router.message(Command("stack"))
async def stack_game_handler(message: Message) -> None:
    result = await send_html_widget(
        chat_id=message.chat.id,
        widget_name="stack",
        height=540,
    )
    if not result.get("ok"):
        logging.error(f"Ошибка sendWidget: {result}")
        await message.answer(f"Ошибка API: <code>{result.get('description')}</code>")
