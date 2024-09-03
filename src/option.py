import ctypes
from tkinter import messagebox

from src.mouse import Mouse


class Option:

    def __init__(self, settings_file):
        self.settings_file = settings_file
        self.mouse = Mouse(settings_file)

    @staticmethod
    def run_as_admin():
        if ctypes.windll.shell32.IsUserAnAdmin():
            print("이미 관리자 권한입니다.")
            return True
        else:
            print("관리자 권한으로 재실행합니다.")
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            return False

    def is_settings_changed(self, x_entry, y_entry, click_type_var):
        current_x = x_entry.get()
        current_y = y_entry.get()
        current_click_type = click_type_var.get()

        saved_data = self.mouse.load_coordinates()
        if saved_data:
            return (str(saved_data["x"]) != current_x or
                    str(saved_data["y"]) != current_y or
                    saved_data["click_type"] != current_click_type)
        return True

    def on_closing(self, root, x_entry, y_entry, click_type_var):
        if self.is_settings_changed(x_entry, y_entry, click_type_var):
            if messagebox.askyesno("설정 저장", "변경된 설정이 있습니다. 저장하시겠습니까?"):
                self.mouse.save_coordinates(x_entry=x_entry, y_entry=y_entry, click_type_var=click_type_var)
        root.destroy()
