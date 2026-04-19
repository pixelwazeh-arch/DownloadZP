def format_progress_bar(percent: float, width: int = 10) -> str:
    filled = int(width * percent / 100)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}]"


def bytes_to_mb(size_bytes: int | float) -> float:
    return round(size_bytes / (1024 * 1024), 2)


def format_speed(speed_bytes: float | None) -> str:
    if speed_bytes is None:
        return "— MB/s"
    return f"{bytes_to_mb(speed_bytes)} MB/s"


def format_eta(eta_seconds: int | None) -> str:
    if eta_seconds is None:
        return "—"
    minutes, seconds = divmod(int(eta_seconds), 60)
    if minutes > 0:
        return f"{minutes}м {seconds}с"
    return f"{seconds}с"


def build_progress_message(d: dict) -> str:
    speed = format_speed(d.get("speed"))
    eta = format_eta(d.get("eta"))

    total = d.get("total_bytes") or d.get("total_bytes_estimate")
    total_str = f"{bytes_to_mb(total)} MB" if total else "? MB"

    downloaded = d.get("downloaded_bytes", 0)
    downloaded_str = f"{bytes_to_mb(downloaded)} MB"

    return (
        f"⏬ <b>Загрузка аудио...</b>\n\n"
        f"📦 Размер: <code>{downloaded_str} / {total_str}</code>\n"
        f"⚡️ Скорость: <code>{speed}</code>\n"
        f"⏱ Осталось: <code>{eta}</code>"
    )