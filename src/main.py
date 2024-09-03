import argparse
import threading
import tkinter as tk
from tkinter import ttk

import keyboard
import pyautogui

from src.day_scheduler import DayScheduler
from src.mouse import Mouse
from src.option import Option
from src.utils import CommonUtils

settings_file = CommonUtils.resolve_file_path("coordinates.json")

mouse = Mouse(settings_file)
option = Option(settings_file)


def update_mouse_position():
    if root.focus_get():
        x, y = pyautogui.position()
        position_label.config(text=f"현재 마우스 위치: {x}, {y}")
    root.after(100, update_mouse_position)


def on_click(x=None, y=None, click_type=None):
    if x is None or y is None or click_type is None:
        x = int(x_entry.get())
        y = int(y_entry.get())
        click_type = click_type_var.get()
    mouse.perform_click(x, y, click_type)


def handle_cli_args():
    parser = argparse.ArgumentParser(description="Auto Clicker CLI options")
    parser.add_argument("--auto-click", action="store_true",
                        help="Automatically perform the click when the program starts")
    args = parser.parse_args()

    return args


def save_mouse_position_by_hotkey():
    if root.focus_get():
        x, y = pyautogui.position()
        x_entry.delete(0, tk.END)
        x_entry.insert(0, x)
        y_entry.delete(0, tk.END)
        y_entry.insert(0, y)


def on_focus(event):
    hotkey_listener = threading.Thread(target=listen_for_hotkey, daemon=True)
    hotkey_listener.start()
    print("App is focused. Hotkey enabled.")


def on_focus_lost(event):
    keyboard.unhook_all_hotkeys()
    print("App is unfocused. Hotkey disabled.")


def listen_for_hotkey():
    if root.focus_get():
        keyboard.add_hotkey('ctrl+s', save_mouse_position_by_hotkey)


def select_days(weekday_vars, day):
    # Update the selected_day variable with the clicked button's day
    tk.StringVar().set(day)

    # Reset all weekday_vars to False
    for day_var in weekday_vars.values():
        day_var.set(False)

    # Set the clicked day to True
    if day in weekday_vars:
        weekday_vars[day].set(True)


def create_gui():
    global x_entry, y_entry, click_type_var, position_label, root

    root = tk.Tk()
    root.title("Auto Clicker")

    tk.Label(root, text="X 좌표:").grid(row=0, column=0)
    x_entry = tk.Entry(root)
    x_entry.grid(row=0, column=1)

    tk.Label(root, text="Y 좌표:").grid(row=1, column=0)
    y_entry = tk.Entry(root)
    y_entry.grid(row=1, column=1)

    tk.Label(root, text="클릭 설정:").grid(row=2, column=0)
    click_type_var = tk.StringVar(value="Click")
    tk.Radiobutton(root, text="클릭", variable=click_type_var, value="Click").grid(row=2, column=1)
    tk.Radiobutton(root, text="더블 클릭", variable=click_type_var, value="DoubleClick").grid(row=2, column=2)

    frame = ttk.Frame(root)
    frame.grid(row=7, column=1)

    ttk.Label(frame, text="시간 (HH:MM:SS):").grid(row=0, column=0, sticky=tk.W)
    time_entry = ttk.Entry(frame)
    time_entry.grid(row=0, column=1)

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

    everyday_button = tk.Button(root, text="매일", command=lambda: select_days(weekday_vars, "everyday"))
    everyday_button.grid(row=8, column=0, columnspan=2)
    weekday_button = tk.Button(root, text="평일", command=lambda: select_days(weekday_vars, "weekday"))
    weekday_button.grid(row=8, column=1, columnspan=2)
    weekend_button = tk.Button(root, text="주말", command=lambda: select_days(weekday_vars, "weekend"))
    weekend_button.grid(row=8, column=2, columnspan=2)

    weekday_frame = ttk.LabelFrame(frame, text="특정 요일 선택")
    weekday_frame.grid(row=2, column=0, columnspan=2)
    for i, (day, var) in enumerate(weekday_vars.items()):
        chk = ttk.Checkbutton(weekday_frame, text=day.capitalize(), variable=var)
        chk.grid(row=0, column=i, sticky=tk.W)

    add_button = ttk.Button(frame, text="스케줄 설정",
                            command=lambda: DayScheduler.add_schedule(time_entry, weekday_vars))
    add_button.grid(row=3, column=0, columnspan=2)

    position_label = tk.Label(root, text="현재 마우스 위치: ")
    position_label.grid(row=3, column=0, columnspan=2)

    click_button = tk.Button(root, text="Click", command=on_click)
    click_button.grid(row=5, column=0, columnspan=2)

    save_button = tk.Button(root, text="Save", command=lambda: mouse.save_coordinates(x_entry, y_entry, click_type_var))
    save_button.grid(row=5, column=1, columnspan=2)

    admin_button = tk.Button(root, text="Re-run as Admin", command=lambda: rerun_as_admin(root))
    admin_button.grid(row=5, column=3, columnspan=3)

    coordinates = mouse.load_coordinates()
    if coordinates:
        x_entry.insert(0, str(coordinates["x"]))
        y_entry.insert(0, str(coordinates["y"]))
        click_type_var.set(coordinates["click_type"])

    update_mouse_position()

    # root.protocol("WM_DELETE_WINDOW", option.on_closing(root, x_entry, y_entry, click_type_var))

    return root


def rerun_as_admin(root):
    root.destroy()
    if option.run_as_admin():
        root = create_gui()

        root.bind("<FocusIn>", on_focus)
        root.bind("<FocusOut>", on_focus_lost)
        root.mainloop()


if __name__ == "__main__":
    root = create_gui()

    scheduler_thread = threading.Thread(target=DayScheduler.run_scheduler, daemon=True)
    scheduler_thread.start()

    root.bind("<FocusIn>", on_focus)
    root.bind("<FocusOut>", on_focus_lost)
    root.mainloop()
