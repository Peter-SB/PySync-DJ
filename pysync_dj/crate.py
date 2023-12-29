import os
from typing import Tuple, List
import parse_serato_crates as parse_serato_crates
from settings import SettingsSingleton

class SeratoCrate:
    def __init__(self, crate_name: str, version: str = '1.0/Serato ScratchLive Crate') -> None:
        """
        Initialize a Serato Crate.

        :param crate_name: The name of the crate.
        :param version: The version of the Serato crate, default is '1.0/Serato ScratchLive Crate'.
        """
        self.version = version
        self.crate_name = crate_name
        self.tracks = []  # List to store track file paths
        self.extra_crate_data = []

    def add_crate_data(self, tag_name: str, data: str) -> None:
        """
        Add extra data to the crate.

        :param tag_name: The name of the tag for the data.
        :param data: The data to be added.
        """
        self.extra_crate_data.append((tag_name, data))

    def add_track(self, file_path: str) -> None:
        """
        Add a track to the crate.

        :param file_path: The file path of the track to be added.
        """
        drive, path_without_drive = os.path.splitdrive(file_path)
        self.tracks.append(('otrk', [('ptrk', path_without_drive)]))

    def remove_first_track(self) -> None:
        """Remove the first track from the crate."""
        if self.tracks:
            self.tracks.pop(0)

    def get_crate_data(self) -> List[Tuple[str, str]]:
        """
        Get the crate data in the format used by Serato.

        :return: A list of tuples representing the crate data.
        """
        crate_data = [('vrsn', self.version)]
        crate_data.extend(self.extra_crate_data)
        crate_data.extend(self.tracks)
        return crate_data

    def save_crate(self) -> None:
        """
        Save the crate to the _Serato_/Subcrates crate folder.
        """
        settings = SettingsSingleton()

        crate_formatted_name = f"PySync DJ%%{self.crate_name}.crate"
        file_path = os.path.join(settings.dj_library_directory, settings.serato_subcrate_dir, crate_formatted_name)
        with open(file_path, 'wb') as f:
            encoded_data = parse_serato_crates.encode_struct(self.get_crate_data())
            f.write(encoded_data)
