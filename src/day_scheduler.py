import time
from tkinter import messagebox

import schedule


class DayScheduler:

    @staticmethod
    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(1)

    @staticmethod
    def schedule_task(func, day=None, time_str="00:00:00", weekdays=None, weekends=None):
        try:
            if day:
                schedule.every().day.at(time_str).do(func).tag(day)
            elif weekdays:
                for day in ["monday", "tuesday", "wednesday", "thursday", "friday"]:
                    schedule.every().day.at(time_str).do(func).tag(day)
            elif weekends:
                for day in ["saturday", "sunday"]:
                    schedule.every().day.at(time_str).do(func).tag(day)
            elif weekdays:
                for day in weekdays:
                    getattr(schedule.every(), day).at(time_str).do(func)
            else:
                schedule.every().week.at(time_str).do(func)
        except schedule.ScheduleValueError as e:
            messagebox.showwarning(title="스케줄 오류", message="유효한 스케줄을 입력하세요.")
            raise schedule.ScheduleValueError(e)

    @staticmethod
    def add_schedule(func, time_entry, schedule_type_var, weekday_vars):
        time_str = time_entry.get()
        schedule_type = schedule_type_var.get()
        selected_days = [day for day, var in weekday_vars.items() if var.get()]

        try:
            if schedule_type == "매주":
                DayScheduler.schedule_task(func=func, time_str=time_str)
            elif schedule_type == "평일":
                DayScheduler.schedule_task(func=func, weekdays=True, time_str=time_str)
            elif schedule_type == "주말":
                DayScheduler.schedule_task(func=func, weekends=True, time_str=time_str)
            elif schedule_type == "특정 요일" and selected_days:
                DayScheduler.schedule_task(func=func, weekdays=selected_days, time_str=time_str)
            else:
                messagebox.showwarning(title="스케줄 오류", message="유효한 스케줄을 입력하세요.")
                return
        except schedule.ScheduleValueError as e:
            return

        messagebox.showinfo(title="스케줄 추가", message="스케줄이 성공적으로 추가되었습니다.")
