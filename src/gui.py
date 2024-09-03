import argparse
import threading
import tkinter as tk
from tkinter import ttk

import keyboard
import pyautogui

from src.day_scheduler import DayScheduler


class Gui:

    _title = "Auto Clicker"

    def __init__(self, root, mouse):
        self.mouse = mouse
        self.root = root
        self.root.title(self._title)

        tk.Label(self.root, text="X 좌표:").grid(row=0, column=0, sticky=tk.W)
        self.x_entry = tk.Entry(self.root)
        self.x_entry.grid(row=0, column=1, sticky=tk.W)

        tk.Label(self.root, text="Y 좌표:").grid(row=1, column=0, sticky=tk.W)
        self.y_entry = tk.Entry(self.root)
        self.y_entry.grid(row=1, column=1, sticky=tk.W)

        tk.Label(self.root, text="클릭 설정:").grid(row=2, column=0)
        self.click_type_var = tk.StringVar(value=mouse.Type.CLICK)
        click_radio = tk.Radiobutton(self.root, text="클릭", variable=self.click_type_var, value=mouse.Type.CLICK)
        click_radio.grid(row=2, column=1, sticky=tk.W)
        double_click_radio = tk.Radiobutton(self.root, text="더블 클릭", variable=self.click_type_var, value=mouse.Type.DOUBLE_CLICK)
        double_click_radio.grid(row=2, column=2, sticky=tk.W)

        self.position_label = tk.Label(self.root, text="현재 마우스 위치 (Ctrl +S 로 저장 가능): ")
        self.position_label.grid(row=3, column=0, columnspan=2, sticky=tk.W)

        click_button = tk.Button(self.root, text="Click", command=self.on_click)
        click_button.grid(row=4, column=0, columnspan=2)

        save_button = tk.Button(self.root, text="Save",
                                command=lambda: mouse.save_coordinates(self.x_entry, self.y_entry, self.click_type_var))
        save_button.grid(row=4, column=1, columnspan=2)

        frame = ttk.Frame(self.root)
        frame.grid(row=5, column=1, sticky=tk.W)

        ttk.Label(frame, text="시간 (HH:MM:SS):").grid(row=0, column=0, sticky=tk.W)
        time_entry = ttk.Entry(frame)
        time_entry.grid(row=0, column=1, sticky=tk.W)

        # 스케줄 타입 선택
        # schedule_type_var = tk.StringVar(value="매주")
        # ttk.Label(frame, text="스케줄 타입:").grid(row=1, column=0, sticky=tk.W)
        # schedule_type_combo = ttk.Combobox(frame, textvariable=schedule_type_var, state="readonly")
        # schedule_type_combo['values'] = ["매주", "평일", "주말", "특정 요일"]
        # schedule_type_combo.grid(row=1, column=1)

        # 특정 요일 선택 (특정 요일을 선택할 때만 활성화)
        weekday_vars = {
            "monday": tk.BooleanVar(),
            "tuesday": tk.BooleanVar(),
            "wednesday": tk.BooleanVar(),
            "thursday": tk.BooleanVar(),
            "friday": tk.BooleanVar(),
            "saturday": tk.BooleanVar(),
            "sunday": tk.BooleanVar(),
        }

        everyday_button = tk.Button(self.root, text="매일", command=lambda: self.select_days(weekday_vars, "everyday"))
        everyday_button.grid(row=8, column=0, columnspan=2)
        weekday_button = tk.Button(self.root, text="평일", command=lambda: self.select_days(weekday_vars, "weekday"))
        weekday_button.grid(row=8, column=1, columnspan=2)
        weekend_button = tk.Button(self.root, text="주말", command=lambda: self.select_days(weekday_vars, "weekend"))
        weekend_button.grid(row=8, column=2, columnspan=2)

        weekday_frame = ttk.LabelFrame(frame, text="특정 요일 선택")
        weekday_frame.grid(row=2, column=0, columnspan=2)
        for i, (day, var) in enumerate(weekday_vars.items()):
            chk = ttk.Checkbutton(weekday_frame, text=day.capitalize(), variable=var)
            chk.grid(row=0, column=i, sticky=tk.W)

        add_button = ttk.Button(frame, text="스케줄 설정",
                                command=lambda: DayScheduler.add_schedule(self.on_click, time_entry, weekday_vars))
        add_button.grid(row=3, column=0, columnspan=2)

        # admin_button = tk.Button(self.root, text="Re-run as Admin", command=lambda: self.rerun_as_admin(self.root))
        # admin_button.grid(row=5, column=3, columnspan=3)

        coordinates = mouse.load_coordinates()
        if coordinates:
            self.x_entry.insert(0, str(coordinates["x"]))
            self.y_entry.insert(0, str(coordinates["y"]))
            self.click_type_var.set(coordinates["click_type"])

        self.update_mouse_position()

    def update_mouse_position(self):
        if self.root.focus_get():
            x, y = pyautogui.position()
            self.position_label.config(text=f"현재 마우스 위치: {x}, {y}")
        self.root.after(100, self.update_mouse_position)

    def on_click(self, x=None, y=None, click_type=None):
        if x is None or y is None or click_type is None:
            x = int(self.x_entry.get())
            y = int(self.y_entry.get())
            click_type = self.click_type_var.get()
        self.mouse.perform_click(x, y, click_type)

    def handle_cli_args(self):
        parser = argparse.ArgumentParser(description="Auto Clicker CLI options")
        parser.add_argument("--auto-click", action="store_true",
                            help="Automatically perform the click when the program starts")
        args = parser.parse_args()

        return args

    def save_mouse_position_by_hotkey(self):
        if self.root.focus_get():
            x, y = pyautogui.position()
            self.x_entry.delete(0, tk.END)
            self.x_entry.insert(0, x)
            self.y_entry.delete(0, tk.END)
            self.y_entry.insert(0, y)

    def on_focus(self, event):
        hotkey_listener = threading.Thread(target=self.listen_for_hotkey, daemon=True)
        hotkey_listener.start()
        print("App is focused. Hotkey enabled.")

    def on_focus_lost(self, event):
        keyboard.unhook_all_hotkeys()
        print("App is unfocused. Hotkey disabled.")

    def listen_for_hotkey(self):
        if self.root.focus_get():
            keyboard.add_hotkey('ctrl+s', self.save_mouse_position_by_hotkey)

    def select_days(self, weekday_vars, day):
        tk.StringVar().set(day)

        for day_var in weekday_vars.values():
            day_var.set(False)

        if day in weekday_vars:
            weekday_vars[day].set(True)

    # def rerun_as_admin(self):
    #     self.root.destroy()
    #     if option.run_as_admin():
    #         self.root = create_gui()
    #
    #         self.root.bind("<FocusIn>", on_focus)
    #         self.root.bind("<FocusOut>", on_focus_lost)
    #         self.root.mainloop()
