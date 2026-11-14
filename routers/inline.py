import asyncio
import hashlib
import logging

import yt_dlp
from aiogram import Router
from aiogram.types import InlineQuery, InlineQueryResultVideo
from yt_dlp.networking.impersonate import ImpersonateTarget

router = Router()


@router.inline_query()
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
