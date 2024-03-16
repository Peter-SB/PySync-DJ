import subprocess
from typing import Optional

import customtkinter as ctk
from tkinter import Menu  # Import Menu from tkinter
from pathlib import Path
import os

import yaml

from pysync_dj import PySyncDJ
from ui_elements.progress_bar import ProgressBar
from ui_elements.ui_output_log import UIOutputLog


class UI:
    def __init__(self):
        # Initialize the customtkinter application
        self.ui_output_log = None
        self.drive_selector = None

        ctk.set_appearance_mode("dark")  # Set the theme to follow the system theme
        ctk.set_default_color_theme("blue")  # Set a color theme
        self.app = ctk.CTk()  # Create the main window
        self.app.title("PySync DJ")  # Set the window title

        self.build_ui()
        self.ui_output_log.log("Starting UX...")

        self.app.mainloop()

    def build_ui(self):
        # Title
        title_label = ctk.CTkLabel(self.app, text="PySync DJ", font=("Roboto", 70))
        title_label.pack(pady=(10, 5))

        # Sub Title
        title_label = ctk.CTkLabel(self.app, text="Sync your Spotify playlists with your DJ libraries", font=("Roboto", 20))
        title_label.pack(pady=(20, 25))

        # Settings Menu
        self.build_menu_bar()

        # Frame for drive selection and download button
        selection_frame = ctk.CTkFrame(self.app)
        selection_frame.pack(pady=14, fill='x', padx=20)

        # Drive Selector
        drive_label = ctk.CTkLabel(selection_frame, text="Drive:")
        drive_label.pack(side='left')

        self.drive_selector = ctk.CTkComboBox(selection_frame, values=self.get_drives())  # Example values
        self.drive_selector.pack(side='left', padx=(5, 20))

        # Download Button
        download_button = ctk.CTkButton(selection_frame, text="Download", command=self.run_main_py)
        download_button.pack(side='right', expand=True, fill='x')

        self.build_progress_bar()

        self.ui_output_log = UIOutputLog(self.app)

    def build_progress_bar(self):
        ProgressBar(self.app)

    def build_menu_bar(self):
        # Tkinter Menu for settings
        menu_bar = Menu(self.app)
        self.app.config(menu=menu_bar)  # Assign the menu to the customtkinter app window
        settings_menu = Menu(menu_bar, tearoff=0)
        settings_menu.add_command(label="Settings", command=self.open_settings)
        menu_bar.add_cascade(label="Menu", menu=settings_menu)

    # Cross-platform method to list available drives/root paths
    @staticmethod
    def get_drives(settings_path: Optional[str] = "../settings.yaml") -> list[str]:
        settings_drive = None

        # Try to read the settings.yaml to find a preferred drive
        try:
            with open(settings_path, 'r') as file:
                settings = yaml.safe_load(file)
                settings_drive = settings.get('dj_library_drive', None)
        except Exception as e:
            print(f"Error reading {settings_path}: {e}")

        drives = []

        if os.name == 'nt':  # Windows specific method
            from ctypes import windll
            bitmask = windll.kernel32.GetLogicalDrives()
            for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                if bitmask & 1:
                    drive_path = f"{letter}:\\"
                    drives.append(drive_path)
                bitmask >>= 1
        else:
            # Unix-like systems
            drives = [str(path) for path in Path("/").iterdir() if path.is_dir()]

        # If a settings drive is specified and exists, prioritize it in the list
        if settings_drive and settings_drive in drives:
            drives.insert(0, drives.pop(drives.index(settings_drive)))
        # elif settings_drive:
        #     # If the drive from settings does not exist in the list (e.g., not mounted), add it at the beginning
        #     drives.insert(0, settings_drive)

        return drives

    # Function to run main.py
    def run_main_py(self):
        # This is a placeholder function that you would replace with the actual code to run main.py
        # For example, you could use subprocess to run the script:
        ProgressBar().set_progress(0)
        self.ui_output_log.log("Starting...")

        selected_drive = self.drive_selector.get()
        pysync_dj = PySyncDJ(selected_drive)
        pysync_dj.run()

        self.ui_output_log.log("Download completed.")

    # Function to open the settings file
    @staticmethod
    def open_settings():
        # Placeholder for opening a settings file. Adjust the file path as needed.
        # For Windows, you could use:
        subprocess.run(["notepad.exe", "../settings.yaml"])
        # For cross-platform compatibility, consider using Python's webbrowser or os module
        print("Opening settings file")


if __name__ == "__main__":
    ui = UI()
