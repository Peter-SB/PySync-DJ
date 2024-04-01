import datetime
import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional

from event_queue import EventQueueHandler
from ui_elements.ui_main import UI
from utils import LOGGER_NAME


class PySyncDJMain:

    def __init__(self):
        self.logger: Optional[logging] = None
        self.ui: Optional[UI] = None

        self.event_queue_handler = EventQueueHandler()

        self.setup_file_logging()
        self.start_ui()

    @staticmethod
    def setup_file_logging():
        def find_log_files(directory):
            matched_files = []
            for filename in os.listdir(directory):
                if filename.startswith("pysync_dj_log_") and filename.endswith(".log"):
                    matched_files.append(os.path.join(directory, filename))
            return matched_files

        log_directory = "../logs"
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)

        # Clean up old log files; ensure only the latest 3 are kept.
        existing_logs = find_log_files(os.path.join(log_directory))
        existing_logs.sort(reverse=True)
        for old_log in existing_logs[2:]:
            os.remove(old_log)

        # Filename with datetime suffix
        datetime_suffix = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_filename = os.path.join(log_directory, f"pysync_dj_log_{datetime_suffix}.log")

        # Set up logging
        logger = logging.getLogger(LOGGER_NAME)
        logger.setLevel(logging.DEBUG)  # Adjust as needed

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)  # Adjust as needed
        console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # File handler with rotation
        file_handler = RotatingFileHandler(log_filename, maxBytes=5 * 1024 * 1024, backupCount=2)
        file_handler.setLevel(logging.DEBUG)  # Adjust as needed
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        return logger

    def start_ui(self):
        self.ui = UI(self.event_queue_handler.event_queue)
        self.event_queue_handler.set_ui(self.ui)

        self.ui.app.after(100, self.event_queue_handler.process_queue())
        self.ui.app.mainloop()


if __name__ == "__main__":
    PySyncDJMain()
