import asyncio
import time
import uuid
from pathlib import Path
from typing import Callable, Awaitable

import yt_dlp

from config import DOWNLOAD_DIR, PROGRESS_UPDATE_INTERVAL, FFMPEG_PATH, FFPROBE_PATH
from utils import build_progress_message


def _get_ydl_opts(output_path: str, progress_hook: Callable) -> dict:
    return {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "ffmpeg_location": FFMPEG_PATH,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "writethumbnail": False,
        "writeinfojson": False,
        "postprocessor_args": [
            "-map_metadata", "-1",
            "-id3v2_version", "3",
        ],
        "progress_hooks": [progress_hook],
    }


async def download_audio(
    url: str,
    on_progress: Callable[[str], Awaitable[None]],
) -> Path:
    file_id = uuid.uuid4().hex
    output_template = str(DOWNLOAD_DIR / f"{file_id}.%(ext)s")

    last_update_time: list[float] = [0.0]
    # get_running_loop() — правильный способ получить loop внутри async функции
    main_loop = asyncio.get_running_loop()

    def progress_hook(d: dict) -> None:
        if d["status"] == "downloading":
            now = time.monotonic()
            if now - last_update_time[0] >= PROGRESS_UPDATE_INTERVAL:
                last_update_time[0] = now
                message = build_progress_message(d)
                asyncio.run_coroutine_threadsafe(on_progress(message), main_loop)

    opts = _get_ydl_opts(output_template, progress_hook)

    def _download() -> str:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(info).rsplit(".", 1)[0] + ".mp3"

    # run_in_executor тоже через main_loop
    mp3_path_str: str = await main_loop.run_in_executor(None, _download)
    mp3_path = Path(mp3_path_str)

    if not mp3_path.exists():
        raise FileNotFoundError(f"Файл не найден после загрузки: {mp3_path}")

    return mp3_path