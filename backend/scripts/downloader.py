import yt_dlp
from pathlib import Path

DOWNLOAD_DIR = Path(r"C:\Users\ramka\Documents\Reel_script_generator_\applicationCode\local\backend\utlis\videos")
COOKIE_FILE = Path(r"C:\Users\ramka\Documents\Reel_script_generator_\applicationCode\local\backend\utlis\cookies\instagram_cookies.txt")

DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)


def download_reel(url):
    print(f"⬇️ Downloading: {url}")

    ydl_opts = {
        'outtmpl': str(DOWNLOAD_DIR / '%(id)s.%(ext)s'),
        'quiet': True,
        'format': 'mp4',

        # ✅ ADD THIS
        'cookiefile': str(COOKIE_FILE),
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filepath = ydl.prepare_filename(info)

        return filepath

    except Exception as e:
        print("❌ Download error:", e)
        return None