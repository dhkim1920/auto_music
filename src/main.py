import threading
import tkinter as tk

from src.day_scheduler import DayScheduler
from src.gui import Gui
from src.mouse import Mouse
from src.option import Option
from src.utils import CommonUtils

settings_file = CommonUtils.resolve_file_path("coordinates.json")

mouse = Mouse(settings_file)
option = Option(settings_file)

if __name__ == "__main__":
    scheduler_thread = threading.Thread(target=DayScheduler.run_scheduler, daemon=True)
    scheduler_thread.start()

    root = tk.Tk()
    app = Gui(root, mouse)
    root.mainloop()
