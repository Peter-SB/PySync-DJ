import customtkinter as ctk
from tkinter import scrolledtext

class UIOutputLog:
    _instance = None  # Class attribute to store the singleton instance

    def __init__(self, app):
        """Private constructor. Use the `get_instance()` class method instead."""
        self.app = app
        self.log_output_box = self.create_output_log_box(app)

    @staticmethod
    def create_output_log_box(app) -> scrolledtext.ScrolledText:
        log_frame = ctk.CTkFrame(app)
        log_frame.pack(fill='both', expand=True, padx=20, pady=(10, 20))

        log_output_box = scrolledtext.ScrolledText(log_frame, height=10, state='disabled')
        log_output_box.pack(fill='both', expand=True)

        log_output_box.config(state='normal')
        log_output_box.config(state='disabled')  # Make it read-only again

        return log_output_box

    @classmethod
    def get_instance(cls, app=None):
        """Get the singleton instance of UIOutputLog. If it doesn't exist, create it."""
        if cls._instance is None:
            if app is None:
                raise ValueError("An 'app' instance must be provided to create UIOutputLog.")
            cls._instance = cls(app)
        return cls._instance

    def log_message(self, message: str, colour: str) -> None:
        self.log_output_box.config(state='normal')
        tag_name = f"color_{colour}"
        self.log_output_box.tag_config(tag_name, foreground=colour)
        self.log_output_box.insert('end', message + '\n', tag_name)
        self.log_output_box.config(state='disabled')
        self.log_output_box.see('end')
        self.app.update()

    def log(self, message: str) -> None:
        self.log_message(message, 'black')

    def alert(self, message: str) -> None:
        self.log_message(message, 'orange')

    def error(self, message: str) -> None:
        self.log_message(message, 'red')