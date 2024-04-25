import logging
import multiprocessing
from typing import Optional

from event_queue import EventQueueHandler
from ui_elements.ui_main import UIMain
from utils import setup_file_logging


class PySyncDJMain:

    def __init__(self):
        self.logger: Optional[logging] = None
        self.ui: Optional[UIMain] = None

        self.event_queue_handler = EventQueueHandler()

        self.logging = setup_file_logging()
        self.start_ui()

    def start_ui(self):
        self.ui = UIMain(self.event_queue_handler.event_queue)
        self.event_queue_handler.set_ui(self.ui)

        self.ui.app.after(250, self.event_queue_handler.process_queue())
        self.ui.app.mainloop()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    PySyncDJMain()
