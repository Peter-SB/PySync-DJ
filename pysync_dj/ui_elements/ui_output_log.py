import customtkinter as ctk
from tkinter import scrolledtext


class UIOutputLog:
    _instance = None

    def __new__(cls, app: ctk.CTk = None):
        """
        UI Logger Output Box for outputting, in the ui, any logs useful to the user.

        :param app: The ui app to add the out logger output box element to.
        """
        if not cls._instance:
            cls._instance = super(UIOutputLog, cls).__new__(cls)
            cls._instance.app = app
            cls._instance.log_output_box = cls._instance.build_ui_elements(app)
        return cls._instance

    @staticmethod
    def build_ui_elements(app: ctk.CTk) -> scrolledtext.ScrolledText:
        """
        Build the logger output box's ui elements

        :param app: the ui app to add the elements to.
        """
        log_frame = ctk.CTkFrame(app)
        log_frame.pack(fill='both', expand=True, padx=20, pady=(10, 20))

        log_output_box = scrolledtext.ScrolledText(log_frame, height=10, state='disabled')
        log_output_box.pack(fill='both', expand=True)

        return log_output_box

    def log_message(self, message: str, colour: str) -> None:
        """
        Log a message to the UI output log box.

        :param message: Message to log out.
        :param colour: Colour of the message using tkinter colours.
        """
        self.log_output_box.config(state='normal')  # Temporarily make it writable to update text

        tag_name = f"color_{colour}"
        self.log_output_box.tag_config(tag_name, foreground=colour)
        self.log_output_box.insert('end', message + '\n', tag_name)
        self.log_output_box.config(state='disabled')

        self.log_output_box.see('end')  # Make it read-only again
        self.app.update()

    def log(self, message: str) -> None:
        """
        Log a black coloured message to the UI output log box.

        :param message: Message to log out.
        """
        self.log_message(message, 'black')

    def info(self, message: str) -> None:
        """
        Log a black coloured info message to the UI output log box.

        :param message: Message to log out.
        """
        self.log_message(message, 'black')

    def alert(self, message: str) -> None:
        """
        Log a orange coloured alert message to the UI output log box.

        :param message: Message to log out.
        """
        self.log_message(message, 'orange')

    def error(self, message: str) -> None:
        """
        Log a red coloured error message to the UI output log box.

        :param message: Message to log out.
        """
        self.log_message(message, 'red')
