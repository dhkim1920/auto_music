from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SETTINGS_FILE = PROJECT_ROOT / "settings.json"
DEFAULT_SCHEDULE_FILE = PROJECT_ROOT / "schedules.json"
DEFAULT_LOG_FILE = PROJECT_ROOT / "auto_music.log"
MIN_YEAR = 2026
MAX_YEAR = 2100


@dataclass
class PixelConfig:
    x: int = 0
    y: int = 0
    r: int = 0
    g: int = 0
    b: int = 0
    tolerance: int = 10
    enabled: bool = False


@dataclass
class AppSettings:
    youtube_music_path: str = ""
    retry_count: int = 1
    play_button_x: int = 0
    play_button_y: int = 0
    login_pixel: PixelConfig = field(default_factory=PixelConfig)
    play_verify_pixel: PixelConfig = field(default_factory=PixelConfig)
    logging_enabled: bool = False
    log_file_path: str = str(DEFAULT_LOG_FILE)
    notify_success: bool = True
    notify_failure: bool = True
    kakao_api_key_file: str = ""

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["login_pixel"] = asdict(self.login_pixel)
        payload["play_verify_pixel"] = asdict(self.play_verify_pixel)
        return payload

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "AppSettings":
        login_pixel = PixelConfig(**raw.get("login_pixel", {}))
        play_verify_pixel = PixelConfig(**raw.get("play_verify_pixel", {}))
        return cls(
            youtube_music_path=raw.get("youtube_music_path", ""),
            retry_count=int(raw.get("retry_count", 1)),
            play_button_x=int(raw.get("play_button_x", 0)),
            play_button_y=int(raw.get("play_button_y", 0)),
            login_pixel=login_pixel,
            play_verify_pixel=play_verify_pixel,
            logging_enabled=bool(raw.get("logging_enabled", False)),
            log_file_path=raw.get("log_file_path", str(DEFAULT_LOG_FILE)),
            notify_success=bool(raw.get("notify_success", True)),
            notify_failure=bool(raw.get("notify_failure", True)),
            kakao_api_key_file=raw.get("kakao_api_key_file", ""),
        )


def load_settings(path: Path = DEFAULT_SETTINGS_FILE) -> AppSettings:
    if not path.exists():
        return AppSettings()
    data = json.loads(path.read_text(encoding="utf-8"))
    return AppSettings.from_dict(data)


def save_settings(settings: AppSettings, path: Path = DEFAULT_SETTINGS_FILE) -> None:
    path.write_text(json.dumps(settings.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")


class ScheduleStore:
    def __init__(self, path: Path = DEFAULT_SCHEDULE_FILE):
        self.path = path
        self._schedules: dict[str, str] = {}
        self.load()

    def load(self) -> None:
        if not self.path.exists():
            self._schedules = {}
            return
        data = json.loads(self.path.read_text(encoding="utf-8"))
        self._schedules = {str(k): str(v) for k, v in data.items()}

    def save(self) -> None:
        self.path.write_text(json.dumps(self._schedules, ensure_ascii=False, indent=2), encoding="utf-8")

    def set_value(self, target_date: date, value: str) -> None:
        self._schedules[target_date.isoformat()] = value

    def get_value(self, target_date: date) -> str:
        return self._schedules.get(target_date.isoformat(), "OFF")

    def all_items(self) -> dict[str, str]:
        return dict(self._schedules)


def is_date_supported(target_date: date) -> bool:
    return MIN_YEAR <= target_date.year <= MAX_YEAR


def configure_logger(settings: AppSettings) -> logging.Logger:
    logger = logging.getLogger("auto_music")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    if settings.logging_enabled:
        log_path = Path(settings.log_file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def load_kakao_api_key(path: str) -> str:
    if not path:
        return ""
    key_path = Path(path)
    if not key_path.exists():
        return ""
    return key_path.read_text(encoding="utf-8").strip()
