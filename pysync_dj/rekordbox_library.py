import logging
from utils import LOGGER_NAME


class RekordboxLibrary:
    """
    A helper class for interacting making m3u playlist firsts for rekordbox.
    """

    def __init__(self) -> None:
        """
        Initializes the RekordboxHelper.

        :param output_path: output_path of m3u files
        """
        self.logger = logging.getLogger(LOGGER_NAME)
        self.tracks = []

    def create_m3u_file(self, output_file: str):
        with open(output_file, 'w') as playlist:
            playlist.write('#EXTM3U\n')  # Header for an extended M3U file
            for file_location in self.tracks:
                playlist.write(file_location + '\n')
