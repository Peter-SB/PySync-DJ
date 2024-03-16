import customtkinter as ctk


class ProgressBar:
    _instance = None

    def __new__(cls, app=None):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.app = app
            cls.progress_bar = cls.build_ui(app)
        return cls._instance

    @staticmethod
    def build_ui(app):
        # Progress Section
        progress_frame = ctk.CTkFrame(app)
        progress_frame.pack(fill='x', padx=20, pady=(10, 0))

        progress_label = ctk.CTkLabel(progress_frame, text="Progress:")
        progress_label.pack(side='left', padx=(0, 10))

        progress_bar = ctk.CTkProgressBar(progress_frame)
        progress_bar.pack(fill='x', padx=20, pady=(10, 20))
        progress_bar.set(0)  # Initialize progress at 0

        return progress_bar

    def set_progress(self, value: float):
        self.progress_bar.set(value)

        # Change color when progress is 100%
        if value >= 1:
            # Assuming there's a method to set color, replace 'set_color' with the actual method
            # And replace 'desired_color' with the actual color you want
            self.progress_bar.configure(progress_color="green2")  # Adjust this line as per actual method available
        else:
            # Reset to default color if progress is less than 100%
            self.progress_bar.configure(progress_color="dodger blue")

        self.progress_bar.update()

