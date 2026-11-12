import os
import asyncio
import re
import hashlib
import logging
import sys
import uuid
import zlib
from pathlib import Path

import aiohttp
import yt_dlp
from yt_dlp.networking.impersonate import ImpersonateTarget
from aiogram import F, Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    InlineQuery,
    InlineQueryResultVideo,
    Message, FSInputFile,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)

from dotenv import load_dotenv

load_dotenv()

WIDGETS_DIR = Path(__file__).parent / "widgets"
TOKEN = os.getenv("BOT_TOKEN")

dp = Dispatcher()


def minify_widget_html(raw_html: str) -> str:
    html = re.sub(r"<!--.*?-->", "", raw_html, flags=re.S)
    lines = [line.strip() for line in html.splitlines() if line.strip()]
    return " ".join(lines)

async def send_html_widget(
    chat_id: int,
    widget_name: str,
    height: int = 540,
    allow_queries: bool = True,
) -> dict:
    widget_path = WIDGETS_DIR / f"{widget_name}.html"
    raw_html = widget_path.read_text(encoding="utf-8")
    compact_html = minify_widget_html(raw_html)

    compressed_size = len(zlib.compress(compact_html.encode("utf-8")))
    logging.info(f"Widget '{widget_name}' compressed size: {compressed_size} / 4096 bytes")

    url = f"https://api.telegram.org/bot{TOKEN}/sendWidget"
    payload = {
        "chat_id": chat_id,
        "html": compact_html,
        "height": height,
        "allow_queries": allow_queries,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            return await resp.json()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    user_id = message.from_user.id
    await message.answer(f"Ваш Telegram ID: <code>{user_id}</code>")


@dp.message(Command("id"))
async def get_user_id_handler(message: Message) -> None:
    user_id = message.from_user.id
    await message.answer(f"Ваш Telegram ID: <code>{user_id}</code>")


@dp.inline_query()
async def inline_query_handler(inline_query: InlineQuery) -> None:
    query = inline_query.query.strip()

    if not query or "instagram.com" not in query:
        return

    result_id = hashlib.md5(query.encode()).hexdigest()

    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'noplaylist': True,
        'quiet': True,
        'impersonate': ImpersonateTarget(client='chrome'),
    }

    try:
        loop = asyncio.get_running_loop()

        def extract_direct_link():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(query, download=False)

        info = await loop.run_in_executor(None, extract_direct_link)

        video_url = info.get('url')
        thumbnail_url = info.get('thumbnail') or "https://via.placeholder.com/300"
        title = info.get('title') or "Instagram Video"
        width = info.get('width', 0)
        height = info.get('height', 0)

        if not video_url:
            return

        results = [
            InlineQueryResultVideo(
                id=result_id,
                title="🎬 Отправить видео",
                video_url=video_url,
                mime_type="video/mp4",
                thumbnail_url=thumbnail_url,
                description=title,
                video_width=width,
                video_height=height
            )
        ]

        await inline_query.answer(results, cache_time=1, is_personal=True)

    except Exception as e:
        logging.error(f"Ошибка в inline_query: {e}")


@dp.message(F.text.contains("instagram.com"))
async def instagram_link_handler(message: Message) -> None:
    status_msg = await message.answer("⏳ Загрузка видео...")
    url = message.text.strip()

    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'noplaylist': True,
        'quiet': True,
        'impersonate': ImpersonateTarget(client='chrome')
    }

    try:
        loop = asyncio.get_running_loop()

        def extract_direct_link():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(url, download=False)

        info = await loop.run_in_executor(None, extract_direct_link)
        video_url = info.get('url')

        if not video_url:
            await status_msg.edit_text("Не удалось найти видео по этой ссылке.")
            return

        await message.answer_video(
            video=video_url,
            caption=""
        )
        await status_msg.delete()

    except Exception as e:
        logging.exception("Детальная ошибка Instagram:")
        await status_msg.edit_text("Произошла ошибка при загрузке видео из Instagram.")


@dp.message(Command("stack"))
async def stack_game_handler(message: Message) -> None:
    result = await send_html_widget(
        chat_id=message.chat.id,
        widget_name="stack",
        height=540,
    )
    if not result.get("ok"):
        logging.error(f"Ошибка sendWidget: {result}")
        await message.answer(f"Ошибка API: <code>{result.get('description')}</code>")

async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")
