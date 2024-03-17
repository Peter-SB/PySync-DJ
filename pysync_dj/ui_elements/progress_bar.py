import customtkinter as ctk


class ProgressBar:
    _instance = None

    def __new__(cls, app: ctk.CTk = None):
        """
        Progress bar for indicating progress of playlist download's progress.

        :param app: The ui app to add the progress bar elements to.
        """
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.app = app
            cls.progress_bar = cls.build_ui_elements(app)
        return cls._instance

    @staticmethod
    def build_ui_elements(app: ctk.CTk):
        """
        Build the progress bar's ui elements

        :param app: the ui app to add the elements to.
        """
        progress_frame = ctk.CTkFrame(app)
        progress_frame.pack(fill='x', padx=20, pady=(10, 0))

        progress_label = ctk.CTkLabel(progress_frame, text="Progress:")
        progress_label.pack(side='left', padx=(0, 10))

        progress_bar = ctk.CTkProgressBar(progress_frame)
        progress_bar.pack(fill='x', padx=20, pady=(10, 20))
        progress_bar.set(0)  # Initialize progress at 0

        return progress_bar

    def set_progress(self, progress: float) -> None:
        """
        Sets the bar's progress. Changes colour to green when progress complete

        :param progress: progress represented by a value 0 to 1.
        """
        self.progress_bar.set(progress)

        if progress >= 1:
            self.progress_bar.configure(progress_color="green2")
        else:
            self.progress_bar.configure(progress_color="dodger blue")

        self.progress_bar.update()

