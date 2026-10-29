import os
import asyncio
import hashlib
import logging
import sys

import yt_dlp
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    InlineQuery,
    InlineQueryResultVideo,
    Message,
)

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

dp = Dispatcher()


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
    ids = []
    query = inline_query.query.strip()
    user_id = inline_query.from_user.id

    if not query or "instagram.com" not in query:
        return
    # if user_id not in ids:
    #     return

    result_id = hashlib.md5(query.encode()).hexdigest()

    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'noplaylist': True,
        'quiet': True,
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


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")