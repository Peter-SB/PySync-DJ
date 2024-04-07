import logging
import os
import urllib

import xml.etree.ElementTree as ET

from mutagen.easyid3 import EasyID3

from dj_libraries.itunes_library import ItunesLibrary
from settings import SettingsSingleton
from utils import LOGGER_NAME


class RekordboxLibrary:
    """
    Helper class for creating M3U playlist files compatible with Rekordbox.
    """

    def __init__(self, playlist_name, downloaded_track_list, file_drive) -> None:
        """
        Initialize the RekordboxLibrary class.
        """
        self.tracks = downloaded_track_list
        self.file_drive = file_drive
        self.playlist_name = playlist_name

    def create_m3u_file(self, output_file_name: str) -> None:
        """
        Create an M3U file with the currently added tracks. The file is saved in the directory specified in the
        SettingsSingleton.

        :param output_file_name: The name of the output M3U file.
        """
        output_file = os.path.join(SettingsSingleton().dj_library_drive,
                                   SettingsSingleton().rekordbox_playlist_folder,
                                   output_file_name)

        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        with open(output_file, 'w') as playlist:
            playlist.write('#EXTM3U\n')  # Header for an extended M3U file
            for file_location in self.tracks:
                playlist.write(os.path.join(self.file_drive, file_location) + '\n')
