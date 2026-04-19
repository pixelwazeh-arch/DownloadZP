import asyncio
import logging
import os
import re

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile

from config import MAX_FILE_SIZE_MB
from downloader import download_audio
from utils import bytes_to_mb

logger = logging.getLogger(__name__)
router = Router()

URL_PATTERN = re.compile(
    r"https?://(www\.)?"
    r"(youtube\.com|youtu\.be|tiktok\.com|vm\.tiktok\.com|music\.youtube\.com)"
    r"\S+",
    re.IGNORECASE,
)


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        "👋 <b>Привет!</b>\n\n"
        "Отправь мне ссылку на видео с <b>YouTube</b> или <b>TikTok</b>, "
        "и я скачаю аудио в формате MP3.\n\n"
        "⚠️ Поддерживаются только публичные видео.",
        parse_mode="HTML",
    )


@router.message(F.text)
async def handle_link(message: Message) -> None:
    text = message.text or ""
    match = URL_PATTERN.search(text)

    if not match:
        await message.answer(
            "❌ Ссылка не распознана.\n"
            "Поддерживаются: <b>YouTube</b> и <b>TikTok</b>.",
            parse_mode="HTML",
        )
        return

    url = match.group(0)
    status_msg = await message.answer(
        "🔍 <b>Анализирую ссылку...</b>", parse_mode="HTML"
    )

    mp3_path = None
    try:
        async def update_progress(text: str) -> None:
            try:
                await status_msg.edit_text(text, parse_mode="HTML")
            except Exception:
                pass

        mp3_path = await download_audio(url, update_progress)

        file_size_mb = bytes_to_mb(os.path.getsize(mp3_path))
        if file_size_mb > MAX_FILE_SIZE_MB:
            await status_msg.edit_text(
                f"❌ Файл слишком большой: <b>{file_size_mb} MB</b>\n"
                f"Лимит Telegram — {MAX_FILE_SIZE_MB} MB.",
                parse_mode="HTML",
            )
            return

        await status_msg.edit_text("📤 <b>Отправляю файл...</b>", parse_mode="HTML")

        audio_file = FSInputFile(mp3_path)
        await message.answer_audio(audio=audio_file)  # caption убран
        await status_msg.delete()

    except Exception as e:
        logger.exception("Unexpected error for %s", url)
        await status_msg.edit_text(
            f"⚠️ <b>Ошибка:</b>\n<code>{e}</code>",
            parse_mode="HTML",
        )
    finally:
        if mp3_path and mp3_path.exists():
            try:
                os.remove(mp3_path)
                logger.info("Удалён временный файл: %s", mp3_path)
            except OSError as e:
                logger.warning("Не удалось удалить файл %s: %s", mp3_path, e)