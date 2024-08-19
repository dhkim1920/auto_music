import sys
import tkinter as tk
from tkinter import messagebox
import pyautogui
import json
import os
import argparse

if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

settings_file = os.path.join(application_path, "coordinates.json")


# 좌표와 클릭 타입 저장
def save_coordinates():
    x = int(x_entry.get())
    y = int(y_entry.get())
    click_type = click_type_var.get()

    data = {
        "x": x,
        "y": y,
        "click_type": click_type
    }

    with open(settings_file, "w") as file:
        json.dump(data, file)

    messagebox.showinfo("설정 저장", "좌표와 클릭 설정이 저장되었습니다.")


# 좌표와 클릭 타입 불러오기
def load_coordinates():
    if os.path.exists(settings_file):
        with open(settings_file, "r") as file:
            data = json.load(file)
        return data
    else:
        messagebox.showinfo("경고", "저장된 좌표를 찾을 수 없습니다.")
        return None


def perform_click(x, y, click_type):
    pyautogui.moveTo(x, y)
    if click_type == "클릭":
        pyautogui.click()
    elif click_type == "더블 클릭":
        pyautogui.doubleClick()


# 현재 마우스 위치 업데이트
def update_mouse_position():
    x, y = pyautogui.position()
    position_label.config(text=f"현재 마우스 위치: {x}, {y}")
    root.after(100, update_mouse_position)  # 100ms 마다 갱신


def on_click(x=None, y=None, click_type=None):
    if x is None or y is None or click_type is None:
        x = int(x_entry.get())
        y = int(y_entry.get())
        click_type = click_type_var.get()
    perform_click(x, y, click_type)


# 명령줄 인수 처리
def handle_cli_args():
    parser = argparse.ArgumentParser(description="Auto Clicker CLI options")
    parser.add_argument("--auto-click", action="store_true",
                        help="Automatically perform the click when the program starts")
    args = parser.parse_args()

    return args


# 설정 값 변경 확인
def is_settings_changed():
    current_x = x_entry.get()
    current_y = y_entry.get()
    current_click_type = click_type_var.get()

    saved_data = load_coordinates()
    if saved_data:
        return (str(saved_data["x"]) != current_x or
                str(saved_data["y"]) != current_y or
                saved_data["click_type"] != current_click_type)
    return True  # If no saved settings, consider settings as changed


def on_closing():
    if is_settings_changed():
        if messagebox.askyesno("설정 저장", "변경된 설정이 있습니다. 저장하시겠습니까?"):
            save_coordinates()
    root.destroy()


def create_gui():
    global x_entry, y_entry, click_type_var, position_label, root

    root = tk.Tk()
    root.title("Auto Clicker")

    # 좌표 입력 필드
    tk.Label(root, text="X 좌표:").grid(row=0, column=0)
    x_entry = tk.Entry(root)
    x_entry.grid(row=0, column=1)

    tk.Label(root, text="Y 좌표:").grid(row=1, column=0)
    y_entry = tk.Entry(root)
    y_entry.grid(row=1, column=1)

    # 클릭 타입 선택
    tk.Label(root, text="클릭 설정:").grid(row=2, column=0)
    click_type_var = tk.StringVar(value="Click")
    tk.Radiobutton(root, text="클릭", variable=click_type_var, value="Click").grid(row=2, column=1)
    tk.Radiobutton(root, text="더블 클릭", variable=click_type_var, value="DoubleClick").grid(row=2, column=2)

    # 현재 마우스 위치 표시 라벨
    position_label = tk.Label(root, text="현재 마우스 위치: ")
    position_label.grid(row=3, column=0, columnspan=2)

    # 클릭 버튼
    click_button = tk.Button(root, text="Click", command=on_click)
    click_button.grid(row=4, column=0, columnspan=2)

    # 저장 버튼
    save_button = tk.Button(root, text="Save", command=save_coordinates)
    save_button.grid(row=4, column=2, columnspan=2)

    coordinates = load_coordinates()
    if coordinates:
        x_entry.insert(0, str(coordinates["x"]))
        y_entry.insert(0, str(coordinates["y"]))
        click_type_var.set(coordinates["click_type"])

    update_mouse_position()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    return root


if __name__ == "__main__":
    args = handle_cli_args()

    if args.auto_click:
        # --auto-click 인수가 전달된 경우 자동 클릭 수행
        coordinates = load_coordinates()
        if coordinates:
            on_click(x=coordinates["x"], y=coordinates["y"], click_type=coordinates["click_type"])
    else:
        # GUI 실행
        root = create_gui()
        root.mainloop()
