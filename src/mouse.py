import json
import os
import time
from enum import Enum
from tkinter import messagebox

import pyautogui
import pydirectinput


class Mouse:
    class Type(Enum):
        CLICK = 0
        DOUBLE_CLICK = 1

    def __init__(self, settings_file):
        self.settings_file = settings_file

    def save_coordinates(self, x_entry, y_entry, click_type_var):
        x = int(x_entry.get())
        y = int(y_entry.get())
        click_type = click_type_var.get()

        data = {
            "x": x,
            "y": y,
            "click_type": click_type
        }

        with open(self.settings_file, "w") as file:
            json.dump(data, file)

        messagebox.showinfo("설정 저장", "좌표와 클릭 설정이 저장되었습니다.")

    def load_coordinates(self):
        if os.path.exists(self.settings_file):
            with open(self.settings_file, "r") as file:
                data = json.load(file)
            return data
        else:
            messagebox.showinfo("경고", "저장된 좌표를 찾을 수 없습니다.")
            return None

    def perform_click(self, x, y, click_type):
        pyautogui.moveTo(x, y)
        time.sleep(0.1)
        pydirectinput.click()
        if click_type == self.Type.CLICK:
            pydirectinput.click()
        elif click_type == self.Type.DOUBLE_CLICK:
            pydirectinput.doubleClick()
