import os
import sys


class CommonUtils:

    @staticmethod
    def resolve_file_path(file_name):
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))

        return os.path.join(application_path, f"../{file_name}")
