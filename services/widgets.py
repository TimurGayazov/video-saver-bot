import logging
import re
import zlib

import aiohttp

from config import settings


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
    widget_path = settings.widgets_dir / f"{widget_name}.html"
    raw_html = widget_path.read_text(encoding="utf-8")
    compact_html = minify_widget_html(raw_html)

    compressed_size = len(zlib.compress(compact_html.encode("utf-8")))
    logging.info(f"Widget '{widget_name}' compressed size: {compressed_size} / 4096 bytes")

    url = f"https://api.telegram.org/bot{settings.bot_token}/sendWidget"
    payload = {
        "chat_id": chat_id,
        "html": compact_html,
        "height": height,
        "allow_queries": allow_queries,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            return await resp.json()
