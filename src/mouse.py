from __future__ import annotations

import logging
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

import psutil
import pyautogui

try:
    from src.utils import AppSettings, PixelConfig
except ModuleNotFoundError:
    from utils import AppSettings, PixelConfig


@dataclass
class AutomationResult:
    success: bool
    reason: str
    attempts: int


class YouTubeMusicAutomation:
    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def _is_process_running(self, executable_path: str) -> bool:
        target = Path(executable_path).name.lower()
        for proc in psutil.process_iter(["name", "exe"]):
            try:
                name = (proc.info.get("name") or "").lower()
                exe = (proc.info.get("exe") or "").lower()
                if target and (name == target or exe.endswith(target)):
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False

    def ensure_process_running(self, settings: AppSettings) -> bool:
        exe_path = settings.youtube_music_path.strip()
        if not exe_path:
            self.logger.error("YouTube Music executable path is empty.")
            return False

        path_obj = Path(exe_path)
        if not path_obj.exists():
            self.logger.error("Executable path does not exist: %s", exe_path)
            return False

        if self._is_process_running(exe_path):
            self.logger.info("YouTube Music process is already running.")
            return True

        try:
            subprocess.Popen([exe_path], shell=False)
            self.logger.info("Launched YouTube Music process.")
            time.sleep(5)
            return True
        except OSError as exc:
            self.logger.exception("Failed to launch process: %s", exc)
            return False

    @staticmethod
    def _pixel_matches(config: PixelConfig) -> bool:
        if not config.enabled:
            return True
        actual = pyautogui.pixel(config.x, config.y)
        return (
            abs(actual[0] - config.r) <= config.tolerance
            and abs(actual[1] - config.g) <= config.tolerance
            and abs(actual[2] - config.b) <= config.tolerance
        )

    def is_logged_in(self, settings: AppSettings) -> bool:
        result = self._pixel_matches(settings.login_pixel)
        if not result:
            self.logger.warning("Login check failed by pixel validation.")
        return result

    def _click_play(self, settings: AppSettings) -> None:
        pyautogui.click(settings.play_button_x, settings.play_button_y)
        self.logger.info("Clicked play button at (%s, %s).", settings.play_button_x, settings.play_button_y)

    def _verify_playback(self, settings: AppSettings) -> bool:
        config = settings.play_verify_pixel
        if config.enabled:
            ok = self._pixel_matches(config)
            if ok:
                self.logger.info("Playback verified by expected icon/pixel state.")
            else:
                self.logger.warning("Playback verification failed.")
            return ok

        # Fallback: detect visible change near play button as a best-effort signal.
        before = pyautogui.screenshot(region=(settings.play_button_x - 5, settings.play_button_y - 5, 10, 10))
        time.sleep(0.5)
        after = pyautogui.screenshot(region=(settings.play_button_x - 5, settings.play_button_y - 5, 10, 10))
        changed = list(before.getdata()) != list(after.getdata())
        if changed:
            self.logger.info("Playback verified by screen change detection.")
        else:
            self.logger.warning("No screen change detected after play click.")
        return changed

    def run(self, settings: AppSettings) -> AutomationResult:
        if not self.ensure_process_running(settings):
            return AutomationResult(False, "프로세스 실행 실패", 0)

        if not self.is_logged_in(settings):
            return AutomationResult(False, "로그인이 되어 있지 않아 재생이 불가능합니다", 0)

        attempts = max(1, settings.retry_count)
        for attempt in range(1, attempts + 1):
            self.logger.info("Playback attempt %s/%s", attempt, attempts)
            self._click_play(settings)
            time.sleep(1.0)
            if self._verify_playback(settings):
                return AutomationResult(True, "음악이 재생되었습니다", attempt)

        return AutomationResult(False, "재생 검증 실패", attempts)


class KakaoNotifierMock:
    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def send(self, api_key: str, message: str) -> None:
        masked = (api_key[:4] + "...") if api_key else "(missing)"
        self.logger.info("[KakaoMock] key=%s message=%s", masked, message)
