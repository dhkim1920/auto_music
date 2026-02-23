from __future__ import annotations

import calendar
from datetime import date, datetime

from apscheduler.schedulers.background import BackgroundScheduler
from PySide6 import QtCore, QtGui, QtWidgets

try:
    from src.mouse import KakaoNotifierMock, YouTubeMusicAutomation
    from src.option import SettingsDialog
    from src.utils import (
        MAX_YEAR,
        MIN_YEAR,
        ScheduleStore,
        configure_logger,
        is_date_supported,
        load_kakao_api_key,
        load_settings,
        save_settings,
    )
except ModuleNotFoundError:
    from mouse import KakaoNotifierMock, YouTubeMusicAutomation
    from option import SettingsDialog
    from utils import (
        MAX_YEAR,
        MIN_YEAR,
        ScheduleStore,
        configure_logger,
        is_date_supported,
        load_kakao_api_key,
        load_settings,
        save_settings,
    )

WEEKDAY_HEADERS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


class SchedulerWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Auto Music Scheduler")
        self.resize(980, 700)

        self.settings = load_settings()
        self.logger = configure_logger(self.settings)
        self.store = ScheduleStore()
        self.automation = YouTubeMusicAutomation(self.logger)
        self.notifier = KakaoNotifierMock(self.logger)

        today = date.today()
        self.current_year = min(MAX_YEAR, max(MIN_YEAR, today.year))
        self.current_month = today.month

        self.scheduler = BackgroundScheduler()
        self.scheduler.start()

        self._build_ui()
        self._render_calendar()
        self._rebuild_jobs()

    def _build_ui(self) -> None:
        central = QtWidgets.QWidget()
        root = QtWidgets.QVBoxLayout(central)

        nav = QtWidgets.QHBoxLayout()
        self.prev_btn = QtWidgets.QPushButton("<")
        self.prev_btn.clicked.connect(self._prev_month)
        self.next_btn = QtWidgets.QPushButton(">")
        self.next_btn.clicked.connect(self._next_month)

        self.year_combo = QtWidgets.QComboBox()
        self.year_combo.addItems([str(year) for year in range(MIN_YEAR, MAX_YEAR + 1)])
        self.year_combo.setCurrentText(str(self.current_year))
        self.year_combo.currentTextChanged.connect(self._jump_to)

        self.month_combo = QtWidgets.QComboBox()
        self.month_combo.addItems([f"{m:02d}" for m in range(1, 13)])
        self.month_combo.setCurrentText(f"{self.current_month:02d}")
        self.month_combo.currentTextChanged.connect(self._jump_to)

        self.settings_btn = QtWidgets.QPushButton("설정")
        self.settings_btn.clicked.connect(self._open_settings)

        self.run_now_btn = QtWidgets.QPushButton("지금 실행")
        self.run_now_btn.clicked.connect(self._run_now)

        nav.addWidget(self.prev_btn)
        nav.addWidget(self.next_btn)
        nav.addWidget(QtWidgets.QLabel("연도"))
        nav.addWidget(self.year_combo)
        nav.addWidget(QtWidgets.QLabel("월"))
        nav.addWidget(self.month_combo)
        nav.addStretch(1)
        nav.addWidget(self.run_now_btn)
        nav.addWidget(self.settings_btn)
        root.addLayout(nav)

        self.calendar_table = QtWidgets.QTableWidget(6, 7)
        self.calendar_table.setHorizontalHeaderLabels(WEEKDAY_HEADERS)
        self.calendar_table.verticalHeader().setVisible(False)
        self.calendar_table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
        self.calendar_table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.calendar_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.calendar_table.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.calendar_table.cellClicked.connect(self._edit_day)
        root.addWidget(self.calendar_table)

        bulk_row = QtWidgets.QHBoxLayout()
        self.bulk_time = QtWidgets.QTimeEdit()
        self.bulk_time.setDisplayFormat("HH:mm")
        self.bulk_time.setTime(QtCore.QTime(8, 0))

        weekday_btn = QtWidgets.QPushButton("평일 일괄")
        weekday_btn.clicked.connect(self._apply_weekday)
        weekend_btn = QtWidgets.QPushButton("주말 일괄")
        weekend_btn.clicked.connect(self._apply_weekend)
        month_btn = QtWidgets.QPushButton("월 일괄")
        month_btn.clicked.connect(self._apply_month)
        year_btn = QtWidgets.QPushButton("년 일괄")
        year_btn.clicked.connect(self._apply_year)

        bulk_row.addWidget(QtWidgets.QLabel("일괄 시간"))
        bulk_row.addWidget(self.bulk_time)
        bulk_row.addWidget(weekday_btn)
        bulk_row.addWidget(weekend_btn)
        bulk_row.addWidget(month_btn)
        bulk_row.addWidget(year_btn)
        bulk_row.addStretch(1)
        root.addLayout(bulk_row)

        hint = QtWidgets.QLabel("날짜 셀을 클릭해 개별 시간(HH:MM) 또는 OFF를 설정하세요.")
        hint.setStyleSheet("color: #666;")
        root.addWidget(hint)

        self.setCentralWidget(central)

    def _jump_to(self) -> None:
        self.current_year = int(self.year_combo.currentText())
        self.current_month = int(self.month_combo.currentText())
        self._render_calendar()

    def _prev_month(self) -> None:
        if self.current_year == MIN_YEAR and self.current_month == 1:
            return
        if self.current_month == 1:
            self.current_year -= 1
            self.current_month = 12
        else:
            self.current_month -= 1
        self._sync_combos()
        self._render_calendar()

    def _next_month(self) -> None:
        if self.current_year == MAX_YEAR and self.current_month == 12:
            return
        if self.current_month == 12:
            self.current_year += 1
            self.current_month = 1
        else:
            self.current_month += 1
        self._sync_combos()
        self._render_calendar()

    def _sync_combos(self) -> None:
        self.year_combo.blockSignals(True)
        self.month_combo.blockSignals(True)
        self.year_combo.setCurrentText(str(self.current_year))
        self.month_combo.setCurrentText(f"{self.current_month:02d}")
        self.year_combo.blockSignals(False)
        self.month_combo.blockSignals(False)

    def _render_calendar(self) -> None:
        self.calendar_table.clearContents()
        first_weekday, day_count = calendar.monthrange(self.current_year, self.current_month)
        start_col = first_weekday

        row = 0
        col = start_col
        today = date.today()

        for day in range(1, day_count + 1):
            target = date(self.current_year, self.current_month, day)
            value = self.store.get_value(target)
            text = f"{day}\n{value}"
            item = QtWidgets.QTableWidgetItem(text)
            item.setData(QtCore.Qt.ItemDataRole.UserRole, target.isoformat())
            item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignLeft)

            if value.upper() == "OFF":
                item.setForeground(QtGui.QColor("#777777"))
            if target == today:
                font = item.font()
                font.setBold(True)
                item.setFont(font)

            self.calendar_table.setItem(row, col, item)
            col += 1
            if col > 6:
                col = 0
                row += 1

    def _edit_day(self, row: int, column: int) -> None:
        item = self.calendar_table.item(row, column)
        if item is None:
            return

        raw_date = item.data(QtCore.Qt.ItemDataRole.UserRole)
        if not raw_date:
            return

        target = date.fromisoformat(raw_date)
        current_value = self.store.get_value(target)
        value, ok = QtWidgets.QInputDialog.getText(
            self,
            "날짜 설정",
            f"{target.isoformat()} 시간(HH:MM) 또는 OFF",
            text=current_value,
        )
        if not ok:
            return

        parsed = value.strip().upper()
        if parsed != "OFF":
            if not self._is_valid_time(parsed):
                QtWidgets.QMessageBox.warning(self, "입력 오류", "시간은 HH:MM 형식 또는 OFF만 가능합니다.")
                return
        self.store.set_value(target, parsed)
        self.store.save()
        self._render_calendar()
        self._rebuild_jobs()

    def _apply_weekday(self) -> None:
        self._apply_for_month(filter_mode="weekday")

    def _apply_weekend(self) -> None:
        self._apply_for_month(filter_mode="weekend")

    def _apply_month(self) -> None:
        self._apply_for_month(filter_mode="all")

    def _apply_year(self) -> None:
        value = self.bulk_time.time().toString("HH:mm")
        for month in range(1, 13):
            _, count = calendar.monthrange(self.current_year, month)
            for day in range(1, count + 1):
                target = date(self.current_year, month, day)
                if is_date_supported(target):
                    self.store.set_value(target, value)
        self.store.save()
        self._render_calendar()
        self._rebuild_jobs()

    def _apply_for_month(self, filter_mode: str) -> None:
        value = self.bulk_time.time().toString("HH:mm")
        _, count = calendar.monthrange(self.current_year, self.current_month)
        for day in range(1, count + 1):
            target = date(self.current_year, self.current_month, day)
            if not is_date_supported(target):
                continue
            weekday = target.weekday()
            if filter_mode == "weekday" and weekday >= 5:
                continue
            if filter_mode == "weekend" and weekday < 5:
                continue
            self.store.set_value(target, value)
        self.store.save()
        self._render_calendar()
        self._rebuild_jobs()

    def _open_settings(self) -> None:
        dialog = SettingsDialog(self.settings, self)
        if dialog.exec() != QtWidgets.QDialog.DialogCode.Accepted:
            return

        self.settings = dialog.to_settings()
        save_settings(self.settings)
        self.logger = configure_logger(self.settings)
        self.automation = YouTubeMusicAutomation(self.logger)
        self.notifier = KakaoNotifierMock(self.logger)
        self.logger.info("Settings updated.")

    def _run_now(self) -> None:
        result = self.automation.run(self.settings)
        self._notify(result.success, result.reason)
        msg = f"결과: {result.reason} (시도: {result.attempts})"
        QtWidgets.QMessageBox.information(self, "실행 결과", msg)

    def _notify(self, success: bool, message: str) -> None:
        key = load_kakao_api_key(self.settings.kakao_api_key_file)
        if success and self.settings.notify_success:
            self.notifier.send(key, message)
        if not success and self.settings.notify_failure:
            self.notifier.send(key, message)

    def _rebuild_jobs(self) -> None:
        self.scheduler.remove_all_jobs()
        now = datetime.now()

        for date_str, value in self.store.all_items().items():
            if value.upper() == "OFF":
                continue
            if not self._is_valid_time(value):
                continue

            target_date = date.fromisoformat(date_str)
            if not is_date_supported(target_date):
                continue

            hour, minute = map(int, value.split(":"))
            run_at = datetime(target_date.year, target_date.month, target_date.day, hour, minute)
            if run_at <= now:
                continue

            self.scheduler.add_job(
                self._run_scheduled,
                trigger="date",
                run_date=run_at,
                id=f"play-{date_str}",
                replace_existing=True,
            )

    def _run_scheduled(self) -> None:
        result = self.automation.run(self.settings)
        self._notify(result.success, result.reason)

    @staticmethod
    def _is_valid_time(value: str) -> bool:
        try:
            datetime.strptime(value, "%H:%M")
            return True
        except ValueError:
            return False

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        save_settings(self.settings)
        self.store.save()
        self.scheduler.shutdown(wait=False)
        event.accept()


def main() -> int:
    app = QtWidgets.QApplication([])
    window = SchedulerWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
