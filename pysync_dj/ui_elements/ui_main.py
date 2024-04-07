import multiprocessing
import subprocess
from multiprocessing import Queue
from typing import Optional

import customtkinter as ctk
from tkinter import Menu
from pathlib import Path
import os

import yaml

from event_queue import EventQueueLogger
from pysync_dj_download import PySyncDJDownload
from ui_elements.ui_progress_bar import UIProgressBar
from ui_elements.ui_output_log import UIOutputLog


class UIMain:
    def __init__(self, event_queue: Queue):
        self.download_button: Optional[ctk.CTkButton] = None
        self.app: Optional[ctk.CTk] = None
        self.ui_output_log: Optional[UIOutputLog] = None
        self.drive_selector: Optional[ctk.CTkComboBox] = None
        self.progress_bar: Optional[UIProgressBar] = None

        self.event_queue = event_queue
        self.event_logger = EventQueueLogger(self.event_queue)

        self.build_ui_app()
        self.build_ui_elements()
        self.event_logger.info("Started. Ready to download.")

    def run_download(self) -> None:
        self.event_logger.update_progress(0)
        selected_drive = self.drive_selector.get()

        self.event_logger.debug("UI Download Button Click")
        self.download_button.configure(state=ctk.DISABLED)

        download_process = multiprocessing.Process(target=PySyncDJDownload, args=(selected_drive, self.event_queue))
        download_process.start()

    def build_ui_app(self) -> None:
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.app = ctk.CTk()
        self.app.title("PySync DJ")

    def build_ui_elements(self) -> None:
        # Build Title
        title_label = ctk.CTkLabel(self.app, text="PySync DJ", font=("Roboto", 70))
        title_label.pack(pady=(10, 5))

        # Build Sub Title
        title_label = ctk.CTkLabel(self.app,
                                   text="Sync your Spotify playlists with your DJ libraries",
                                   font=("Roboto", 20))
        title_label.pack(pady=(20, 25))

        # Build Settings Menu
        self.build_menu_bar_element()

        # Build Frame for drive selection and download button
        selection_frame = ctk.CTkFrame(self.app)
        selection_frame.pack(pady=14, fill='x', padx=20)

        # Build Drive Selector
        drive_label = ctk.CTkLabel(selection_frame, text="Drive:")
        drive_label.pack(side='left')

        self.drive_selector = ctk.CTkComboBox(selection_frame, values=self.get_drives())  # Example values
        self.drive_selector.pack(side='left', padx=(5, 20))

        # Build Download Button
        self.download_button = ctk.CTkButton(selection_frame, text="Download", command=self.run_download)
        self.download_button.pack(side='right', expand=True, fill='x')

        # Build Progress Bar
        self.progress_bar = UIProgressBar(self.app)

        # Build UI Logger Output
        self.ui_output_log = UIOutputLog(self.app)

    def build_menu_bar_element(self) -> None:
        menu_bar = Menu(self.app)
        self.app.config(menu=menu_bar)
        settings_menu = Menu(menu_bar, tearoff=0)
        settings_menu.add_command(label="Settings", command=self.open_settings)
        menu_bar.add_cascade(label="Menu", menu=settings_menu)

    @staticmethod
    def get_drives(settings_path: Optional[str] = "../settings.yaml") -> list[str]:
        """
        List available drives for selecting download locations.

        :param settings_path: Location of settings.yaml file.
        """
        settings_drive = None

        # Try to read the settings.yaml to find a preferred drive
        try:
            with open(settings_path, 'r') as file:
                settings = yaml.safe_load(file)
                settings_drive = settings.get('dj_library_drive', None)
        except Exception as e:
            print(f"Error reading {settings_path}: {e}")

        drives = []

        # Select dives on Windows systems
        if os.name == 'nt':
            from ctypes import windll
            bitmask = windll.kernel32.GetLogicalDrives()
            for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                if bitmask & 1:
                    drive_path = f"{letter}:\\"
                    drives.append(drive_path)
                bitmask >>= 1
        # Select dives on Unix systems
        else:
            drives = [str(path) for path in Path("/").iterdir() if path.is_dir()]

        # If the specified drive exists, add it to the top of the list
        if settings_drive and settings_drive in drives:
            drives.insert(0, drives.pop(drives.index(settings_drive)))

        return drives

    @staticmethod
    def open_settings() -> None:
        """
        Opens the setting in notepad for windows users
        """
        subprocess.run(["notepad.exe", "../settings.yaml"])

