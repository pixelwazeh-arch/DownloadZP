import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env файле!")

# Папка для временного хранения файлов
DOWNLOAD_DIR: Path = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

# Путь к локальной папке ffmpeg
BASE_DIR: Path = Path(__file__).parent
FFMPEG_DIR: Path = BASE_DIR / "ffmpeg-8.1" / "bin"

# Определяем имя исполняемого файла в зависимости от ОС
_exe = ".exe" if sys.platform == "win32" else ""
FFMPEG_PATH: str = str(FFMPEG_DIR / f"ffmpeg{_exe}")
FFPROBE_PATH: str = str(FFMPEG_DIR / f"ffprobe{_exe}")

# Проверяем, что ffmpeg найден
if not Path(FFMPEG_PATH).exists():
    raise FileNotFoundError(
        f"ffmpeg не найден по пути: {FFMPEG_PATH}\n"
        f"Убедись, что папка ffmpeg-8.1/bin/ существует рядом с main.py"
    )

# Максимальный размер файла для отправки через Telegram (50 MB)
MAX_FILE_SIZE_MB: int = 50

# Интервал обновления прогресс-бара (секунды)
PROGRESS_UPDATE_INTERVAL: float = 1.75