import os
import parse_serato_crates as parse_serato_crates
from settings import SettingsSingleton


class SeratoCrate:
    def __init__(self, create_name:str, version:str ='1.0/Serato ScratchLive Crate'):
        self.version = version
        self.create_name = create_name
        self.tracks = []  # List to store track file paths
        self.extra_crate_data = []

    # @staticmethod
    # def load_crate(create_name: str):
    #     file_location = os.path.join(config.dj_library_directory, config.tracks_folder, create_name)
    #     if create := parse_serato_crates.load_crate(file_location):
    #         pass

    def add_crate_data(self, tag_name, data):
        """Add data to the crate."""
        self.tracks.append((tag_name, data))

    def add_track(self, file_path):
        """Add a track to the crate."""
        drive, path_without_drive = os.path.splitdrive(file_path)
        self.tracks.append(('otrk', [('ptrk', path_without_drive)]))

    def remove_first_track(self):
        """Remove the first track from the crate."""
        if self.tracks:
            self.tracks.pop(0)

    def get_crate_data(self):
        """Get the crate data in the format used by Serato."""
        crate_data = [('vrsn', self.version)]
        crate_data.extend(self.tracks)
        return crate_data

    def save_crate(self):
        """Save the crate to _Serato_-\Subcrates crate folder"""
        subcrate_dir = "_Serato_\Subcrates"
        crate_formatted_name = f"SpotifyDL%%{self.create_name}.crate"
        file_path = os.path.join(SettingsSingleton().dj_library_directory, subcrate_dir, crate_formatted_name)
        with open(file_path, 'wb') as f:
            encoded_data = parse_serato_crates.encode_struct(self.get_crate_data())
            f.write(encoded_data)

