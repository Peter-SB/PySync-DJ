import logging
import multiprocessing
from queue import Queue
from typing import Optional
import customtkinter as ctk

from utils import LOGGER_NAME


class EventQueueHandler:
    """
    This handles the events queue allowing custom logging and progress bar update across
    multiple progresses and sub processes.
    """

    def __init__(self):
        self.manager: multiprocessing.Manager = multiprocessing.Manager()
        self.event_queue: Queue = self.manager.Queue(-1)

        self.ui: Optional['UI'] = None
        self.logger = logging.getLogger(LOGGER_NAME)

    def __exit__(self):
        if self.manager:
            self.manager.shutdown()

    def set_ui(self, ui: 'UI') -> None:
        self.ui = ui

    def process_queue(self) -> None:
        """
        Run periodically by the UI, this function will check the queue until empty and runs the relevant
        event function and passes the data.
        """
        handled_queue_events = {
            "update_progress": self.update_progress,
            "log_debug": self.log_debug,
            "log_info": self.log_info,
            "log_error": self.log_error,
            "enable_download_button": self.enable_download_button
        }

        # Process all available messages in the queue
        while not self.event_queue.empty():
            try:
                event_type, data = self.event_queue.get_nowait()
                handler = handled_queue_events.get(event_type)
                if handler:
                    handler(data)
                else:
                    self.logger.error(f"Unknown message type:{event_type}")

            except Exception:
                import sys, traceback
                self.logger.error(f"Queue error")
                print('Whoops! Problem:', file=sys.stderr)
                traceback.print_exc(file=sys.stderr)

        # Schedule the next check of the event queue
        if self.ui:
            self.ui.app.after(100, self.process_queue)

    def enable_download_button(self, data) -> None:
        self.ui.download_button.configure(state=ctk.NORMAL)

    def update_progress(self, progress: float) -> None:
        self.ui.progress_bar.set_progress(progress)

    def log_debug(self, message: str) -> None:
        print(message)
        self.logger.debug(message)

    def log_info(self, message: str) -> None:
        print(message)
        self.logger.info(message)
        self.ui.ui_output_log.info(message)

    def log_error(self, message: str) -> None:
        print(message)
        self.logger.error(message)
        self.ui.ui_output_log.error(message)


class EventQueueLogger:
    """
    Act as a logger class for adding to the events queue
    """

    def __init__(self, queue):
        self.queue = queue

    def debug(self, message: str) -> None:
        self.queue.put(("log_debug", message))

    def info(self, message: str) -> None:
        self.queue.put(("log_info", message))

    def error(self, message: str) -> None:
        self.queue.put(("log_error", message))

    def update_progress(self, progress: float) -> None:
        self.queue.put(("update_progress", progress))

    def enable_download_button(self) -> None:
        self.queue.put(("enable_download_button", None))


def update_progress_bar(queue, progress: float) -> None:
    """
    Static function for updating the progress bar
    """
    queue.put(("update_progress", progress))
