import asyncio
import logging

import yt_dlp
from aiogram import F, Router
from aiogram.types import Message
from yt_dlp.networking.impersonate import ImpersonateTarget

router = Router()


@router.message(F.text.contains("instagram.com"))
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
