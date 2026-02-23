from datetime import date
from pathlib import Path

from src.utils import AppSettings, PixelConfig, ScheduleStore, load_settings, save_settings


def test_settings_roundtrip(tmp_path: Path):
    settings_file = tmp_path / "settings.json"
    settings = AppSettings(
        youtube_music_path="C:/Program Files/YouTube Music/ytmusic.exe",
        retry_count=3,
        play_button_x=100,
        play_button_y=200,
        login_pixel=PixelConfig(x=1, y=2, r=3, g=4, b=5, tolerance=8, enabled=True),
        play_verify_pixel=PixelConfig(x=10, y=20, r=30, g=40, b=50, tolerance=5, enabled=True),
        logging_enabled=True,
        log_file_path=str(tmp_path / "app.log"),
        notify_success=True,
        notify_failure=False,
        kakao_api_key_file=str(tmp_path / "key.txt"),
    )

    save_settings(settings, settings_file)
    loaded = load_settings(settings_file)

    assert loaded.youtube_music_path == settings.youtube_music_path
    assert loaded.retry_count == 3
    assert loaded.login_pixel.enabled is True
    assert loaded.play_verify_pixel.r == 30


def test_schedule_store_set_get(tmp_path: Path):
    schedule_file = tmp_path / "schedules.json"
    store = ScheduleStore(schedule_file)

    target = date(2026, 1, 15)
    store.set_value(target, "08:30")
    store.save()

    reloaded = ScheduleStore(schedule_file)
    assert reloaded.get_value(target) == "08:30"
    assert reloaded.get_value(date(2026, 1, 16)) == "OFF"
