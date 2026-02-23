from __future__ import annotations

from pathlib import Path

from PySide6 import QtWidgets

try:
    from src.utils import AppSettings, PixelConfig
except ModuleNotFoundError:
    from utils import AppSettings, PixelConfig


class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, settings: AppSettings, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("설정")
        self.setModal(True)
        self._settings = settings

        form = QtWidgets.QFormLayout(self)

        self.path_edit = QtWidgets.QLineEdit(settings.youtube_music_path)
        path_btn = QtWidgets.QPushButton("찾기")
        path_btn.clicked.connect(self._pick_exe)
        path_row = QtWidgets.QHBoxLayout()
        path_row.addWidget(self.path_edit)
        path_row.addWidget(path_btn)
        path_wrap = QtWidgets.QWidget()
        path_wrap.setLayout(path_row)
        form.addRow("YouTube Music 경로", path_wrap)

        self.retry_spin = QtWidgets.QSpinBox()
        self.retry_spin.setRange(1, 10)
        self.retry_spin.setValue(settings.retry_count)
        form.addRow("재시도 횟수", self.retry_spin)

        self.play_x = QtWidgets.QSpinBox()
        self.play_x.setRange(0, 99999)
        self.play_x.setValue(settings.play_button_x)
        self.play_y = QtWidgets.QSpinBox()
        self.play_y.setRange(0, 99999)
        self.play_y.setValue(settings.play_button_y)
        play_row = QtWidgets.QHBoxLayout()
        play_row.addWidget(self.play_x)
        play_row.addWidget(self.play_y)
        play_wrap = QtWidgets.QWidget()
        play_wrap.setLayout(play_row)
        form.addRow("Play 버튼 좌표 X/Y", play_wrap)

        self.login_group = self._build_pixel_group("로그인 픽셀", settings.login_pixel)
        form.addRow(self.login_group)

        self.play_group = self._build_pixel_group("재생 검증 픽셀", settings.play_verify_pixel)
        form.addRow(self.play_group)

        self.log_enabled = QtWidgets.QCheckBox("로깅 사용")
        self.log_enabled.setChecked(settings.logging_enabled)
        form.addRow(self.log_enabled)

        self.log_path_edit = QtWidgets.QLineEdit(settings.log_file_path)
        log_btn = QtWidgets.QPushButton("찾기")
        log_btn.clicked.connect(self._pick_log)
        log_row = QtWidgets.QHBoxLayout()
        log_row.addWidget(self.log_path_edit)
        log_row.addWidget(log_btn)
        log_wrap = QtWidgets.QWidget()
        log_wrap.setLayout(log_row)
        form.addRow("로그 파일", log_wrap)

        self.success_alarm = QtWidgets.QCheckBox("성공 알림")
        self.success_alarm.setChecked(settings.notify_success)
        self.failure_alarm = QtWidgets.QCheckBox("실패 알림")
        self.failure_alarm.setChecked(settings.notify_failure)
        form.addRow(self.success_alarm)
        form.addRow(self.failure_alarm)

        self.key_edit = QtWidgets.QLineEdit(settings.kakao_api_key_file)
        key_btn = QtWidgets.QPushButton("찾기")
        key_btn.clicked.connect(self._pick_key)
        key_row = QtWidgets.QHBoxLayout()
        key_row.addWidget(self.key_edit)
        key_row.addWidget(key_btn)
        key_wrap = QtWidgets.QWidget()
        key_wrap.setLayout(key_row)
        form.addRow("Kakao API Key 파일", key_wrap)

        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

        self._toggle_log_path(self.log_enabled.isChecked())
        self.log_enabled.toggled.connect(self._toggle_log_path)

    def _build_pixel_group(self, title: str, config: PixelConfig) -> QtWidgets.QGroupBox:
        group = QtWidgets.QGroupBox(title)
        layout = QtWidgets.QFormLayout(group)

        enabled = QtWidgets.QCheckBox("사용")
        enabled.setChecked(config.enabled)

        x = QtWidgets.QSpinBox()
        x.setRange(0, 99999)
        x.setValue(config.x)
        y = QtWidgets.QSpinBox()
        y.setRange(0, 99999)
        y.setValue(config.y)

        r = QtWidgets.QSpinBox()
        r.setRange(0, 255)
        r.setValue(config.r)
        g = QtWidgets.QSpinBox()
        g.setRange(0, 255)
        g.setValue(config.g)
        b = QtWidgets.QSpinBox()
        b.setRange(0, 255)
        b.setValue(config.b)

        tolerance = QtWidgets.QSpinBox()
        tolerance.setRange(0, 255)
        tolerance.setValue(config.tolerance)

        pos_row = QtWidgets.QHBoxLayout()
        pos_row.addWidget(x)
        pos_row.addWidget(y)
        pos_wrap = QtWidgets.QWidget()
        pos_wrap.setLayout(pos_row)

        rgb_row = QtWidgets.QHBoxLayout()
        rgb_row.addWidget(r)
        rgb_row.addWidget(g)
        rgb_row.addWidget(b)
        rgb_wrap = QtWidgets.QWidget()
        rgb_wrap.setLayout(rgb_row)

        layout.addRow(enabled)
        layout.addRow("좌표 X/Y", pos_wrap)
        layout.addRow("RGB", rgb_wrap)
        layout.addRow("허용 오차", tolerance)

        group.setProperty("enabled_chk", enabled)
        group.setProperty("x", x)
        group.setProperty("y", y)
        group.setProperty("r", r)
        group.setProperty("g", g)
        group.setProperty("b", b)
        group.setProperty("tol", tolerance)
        return group

    @staticmethod
    def _read_pixel_group(group: QtWidgets.QGroupBox) -> PixelConfig:
        return PixelConfig(
            enabled=group.property("enabled_chk").isChecked(),
            x=group.property("x").value(),
            y=group.property("y").value(),
            r=group.property("r").value(),
            g=group.property("g").value(),
            b=group.property("b").value(),
            tolerance=group.property("tol").value(),
        )

    def _toggle_log_path(self, enabled: bool) -> None:
        self.log_path_edit.setEnabled(enabled)

    def _pick_exe(self) -> None:
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "실행 파일 선택", "", "Executable (*.exe)")
        if file_path:
            self.path_edit.setText(file_path)

    def _pick_log(self) -> None:
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "로그 파일 저장", "auto_music.log", "Log (*.log)")
        if file_path:
            self.log_path_edit.setText(file_path)

    def _pick_key(self) -> None:
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "API Key 파일 선택", "", "Text (*.txt);;All Files (*)")
        if file_path:
            self.key_edit.setText(file_path)

    def to_settings(self) -> AppSettings:
        return AppSettings(
            youtube_music_path=self.path_edit.text().strip(),
            retry_count=self.retry_spin.value(),
            play_button_x=self.play_x.value(),
            play_button_y=self.play_y.value(),
            login_pixel=self._read_pixel_group(self.login_group),
            play_verify_pixel=self._read_pixel_group(self.play_group),
            logging_enabled=self.log_enabled.isChecked(),
            log_file_path=self.log_path_edit.text().strip() or str(Path("auto_music.log").resolve()),
            notify_success=self.success_alarm.isChecked(),
            notify_failure=self.failure_alarm.isChecked(),
            kakao_api_key_file=self.key_edit.text().strip(),
        )
