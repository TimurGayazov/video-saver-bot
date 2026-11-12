import yt_dlp
from yt_dlp.networking.impersonate import ImpersonateTarget


def download_tiktok(url):
  ydl_opts = {
      # Получаем лучшую доступную версию в формате mp4
      'format': 'best[ext=mp4]',
      'quiet': False,
      'noplaylist': True,
      'impersonate': ImpersonateTarget(client='chrome')
  }

  with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    # Извлекаем информацию о видео без скачивания, чтобы узнать прямую ссылку
    info_dict = ydl.extract_info(url, download=False)
    direct_video_url = info_dict.get('url', None)

    print(f'Прямая ссылка на видео: {direct_video_url}')

    # Скачивание видео
    ydl.download([url])


# Пример ссылки на видео TikTok
# video_url = 'https://vt.tiktok.com/ZSpMAEQyd/'
# video_url = 'https://www.instagram.com/reel/DeNTjEMNvXJ/?vrfl=MWp2NmNtb3pjcnhzdA=='
video_url = 'https://youtube.com/shorts/klyPt9Ilqc4?si=bUH1dR8x9AI5Ucrm'
download_tiktok(video_url)