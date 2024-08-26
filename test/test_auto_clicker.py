import unittest
from unittest.mock import patch, mock_open
import tkinter as tk
import json

from src.main import create_gui, save_coordinates, load_coordinates, on_click, settings_file


class TestAutoClicker(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.gui = create_gui()
        self.root.update()

    def tearDown(self):
        self.root.destroy()

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists", return_value=True)
    def test_load_coordinates(self, mock_file):
        mock_file.return_value.read.return_value = json.dumps({"x": 100, "y": 200, "click_type": "Click"})

        data = load_coordinates()
        self.assertEqual(data["x"], 100)
        self.assertEqual(data["y"], 200)
        self.assertEqual(data["click_type"], "Click")

    @patch("builtins.open", new_callable=mock_open)
    def test_save_coordinates(self, mock_file):
        x_entry = self.gui.children['!entry']
        y_entry = self.gui.children['!entry2']
        x_entry.insert(0, '300')
        y_entry.insert(0, '400')

        click_type_var = self.gui.children['!radiobutton'].cget('variable')
        click_type_var.set('DoubleClick')

        save_coordinates()

        mock_file.assert_called_once_with(settings_file, 'w')
        handle = mock_file()
        handle.write.assert_called_once_with(json.dumps({"x": 300, "y": 400, "click_type": "DoubleClick"}))

    @patch("pyautogui.click")
    @patch("pyautogui.moveTo")
    def test_on_click(self, mock_move, mock_click):
        # Set entries in the GUI
        x_entry = self.gui.children['!entry']
        y_entry = self.gui.children['!entry2']
        x_entry.insert(0, '500')
        y_entry.insert(0, '600')

        click_type_var = self.gui.children['!radiobutton'].cget('variable')
        click_type_var.set('Click')

        on_click()
        mock_move.assert_called_once_with(500, 600)
        mock_click.assert_called_once()


if __name__ == '__main__':
    unittest.main()
