import customtkinter as ctk
from tkinter import scrolledtext


class UIOutputLog:
    _instance = None

    def __new__(cls, app=None):
        if not cls._instance:
            cls._instance = super(UIOutputLog, cls).__new__(cls)
            cls._instance.app = app
            cls._instance.log_output_box = cls._instance.create_output_log_box(app)
        return cls._instance

    @staticmethod
    def create_output_log_box(app) -> scrolledtext.ScrolledText:
        log_frame = ctk.CTkFrame(app)
        log_frame.pack(fill='both', expand=True, padx=20, pady=(10, 20))

        log_output_box = scrolledtext.ScrolledText(log_frame, height=10, state='disabled')
        log_output_box.pack(fill='both', expand=True)

        log_output_box.config(state='normal')  # Temporarily make it writable to update text
        log_output_box.config(state='disabled')  # Make it read-only again

        return log_output_box

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

    def info(self, message: str) -> None:
        self.log_message(message, 'black')

    def alert(self, message: str) -> None:
        self.log_message(message, 'orange')

    def error(self, message: str) -> None:
        self.log_message(message, 'red')
